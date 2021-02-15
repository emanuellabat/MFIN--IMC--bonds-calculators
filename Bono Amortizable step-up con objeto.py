# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 13:43:12 2020

@author: Emanuel
"""

import pandas as pd #pandas es una libreria que permite trabajar con datos
import datetime #libreria para manejo de fechas
import numpy as np #libreria para operaciones con matrices, polinomios, entre otros 
from dateutil.relativedelta import relativedelta #funcion para poder realizar operaciones con fechas



class Bond_valuator:
    def __init__(self,
                 HC,
                 amort,
                 cup,
                 cap,
                 ytm,
                 F_Liqui,
                 F_Venc,
                 F_dev_CI,
                 F_pago_CI):
        self.HC = HC
        self.amort=amort
        self.cup=cup
        self.cap=cap
        self.ytm=ytm
        self.F_Liqui=F_Liqui
        self.F_Venc=F_Venc
        self.F_dev_CI=F_dev_CI
        self.F_pago_CI=F_pago_CI
    
    
    def dates(self):
        
        year_frac=[]
        Fechas=[self.F_Venc]
        
        if self.cap == 2:
            DD=relativedelta(months=6)
        else:
            DD=relativedelta(years=1) 
               
        f=self.F_Venc- DD
        
        while f >= self.F_pago_CI:
            Fechas.insert(0,f)
            f=f - DD
            
        #Se calculan los dias para descontar como la diferencia entre la fecha de pago del bono y la fecha de valorización
        for i in range(0,len(Fechas)):
            t=Fechas[i]-self.F_Liqui
            year_frac.append(t.days/365)
        
        self.Fechas=Fechas
        self.year_frac=year_frac
            
        return Fechas, year_frac
    
        '''
        
        El metodo "date" me permite calcular la lista de fechas y fraciones de año que hay entre un pago de cupon y el siguiente.
        
        Los inputs de este metodo, son:
            * son las propiedades del objeto
        
        
        year_frac = si es capitalizacion anual se toma el delta de 1 año y si es capitalizacion semi-anual se toma el delta de 6 meses.
        
        Fechas = inicio la lista desde la fecha que se empieza a liquidar (es un input del objeto) y le voy agregando el delta en base a si es 
                capitalizacion anual o semi-anual.
        
        
        Los returns son:
            * lista de Fechas
            * lista de year_frac
        
      
        '''

    def cup_and_prin(self, df1):
        
        self.df1 = df1

        Cupon=[0]*len(self.Fechas)
        #Cupon=[self.cup/self.cap]*len(self.Fechas)
        Principal=[0]*len(self.Fechas)  
        new_list=[0]*len(self.Fechas) 
        
        
        #-----creo la lista de los principales---------------------
        Amort=self.amort
        j=0
        while j < Amort:
            new_list[2*j] = self.HC/self.amort
            j=j+1
        
        Principal=new_list[::-1]
        
        #-----creo la lista de los cupones---------------------
        
        total  = 0
        sums   = [0]                                                #lo inicializo con un valor 0 y luego agrego para que me quede bien en el valor de Cupon
        
        for v in Principal:
             total = total + v
             sums.append(total)
        
        '''
        
        Armo 2 data frame para poder armar la estructura de los cupones, es PARA EL STEP-UP DE BONOS, es decir, que armo
        2 data frame para luego armar una lista con los cupones que necesito porque uso la funcion merge_asof de panda
        que en base a un columna de un DF me une los valores de otra en la primera.     
        
        '''
        
        self.df1['Fecha']=pd.to_datetime(self.df1.Fecha)                       #es para pasar la fecha de str a formato de fecha datetime
        df2 = pd.DataFrame({'Fecha' : self.Fechas})
        
        df = pd.merge_asof(df2, df1, on='Fecha', allow_exact_matches= False)
        
        vector_stepup=df['Cupon']                                              #es el vector con los cupones step-up en base a la estructura de cupones
        
        for i in range(0, len(self.Fechas)):
            Cupon[i]=np.round((vector_stepup[i]/self.cap*(self.HC-sums[i]))/100,2)
        
        
        self.Cupon=Cupon
        self.Principal=Principal
                    
        return Cupon, Principal
    
        '''
        
        El metodo "cup_and_prin" me permite calcular la lista de los cupones y principal.
        
        Los inputs de este metodo, son:
            * lista de fechas
        
        
        Precio= Cupon + Principal
        
                               Flujo i
        Flujo dscto =  -----------------------
                       (1 + YTM/cap)^(cap * Ti)
        
        
        Los returns son:
            * lista de Cupon
            * lista de Principal
        
        '''
    
    def flujos(self):    
                     
        Flujo=[]
        Flujo_dscto=[]

        #---------Se calculan los flujos------------------
        for i in range(0,len(self.Fechas)):
            Flujo.append(self.Cupon[i]+self.Principal[i])
         
        
        #--------Se calculan los flujos descontados------------
        
        for i in range(0,len(self.Fechas)):
            Flujo_dscto.append(np.round(Flujo[i]/np.power(1+(self.ytm/100)/self.cap,self.cap*self.year_frac[i]),3))
        
        
        self.Flujo=Flujo
        self.Flujo_dscto=Flujo_dscto
        
        return Flujo, Flujo_dscto
    
        '''
        
        El metodo "Flujos" me permite calcular los flujos (Cupon + Principal) y el flujo descontado a valor presente usando la YTM.
        
        Los inputs de este metodo, son:
            * lista de fechas
            * lista de fraccion de año
            * lista de Cupon
            * lista de Principal
        
        
        Precio= Cupon + Principal
        
                               Flujo i
        Flujo dscto =  -----------------------
                       (1 + YTM/cap)^(cap * Ti)
        
        
        Los returns son:
            * lista de Flujo (Cupon + Principal)
            * lista de Flujos descontados
            
        '''
        
    def bond_values(self):
        

        Duracion_list=[]
        Convexidad_list=[]
        
        Precio=np.round(np.sum(self.Flujo_dscto),2)

        #-------Calculando Duration y Convexidad del bono------------------
        
        for i in range(0,len(self.Fechas)):
            Duracion_list.append(np.round((self.Flujo_dscto[i]/Precio)*self.year_frac[i],3))
            Convexidad_list.append(np.round((self.Flujo_dscto[i]/Precio)*np.power(self.year_frac[i],2),3))
              
            
        Duracion=np.round(np.sum(Duracion_list)/(1+(self.ytm/100/self.cap)),2)
        Convexidad=np.round(np.sum(Convexidad_list),2)                          # Hago la suma de la lista de Convexidad para mostrar el valor final

        
        self.Precio=Precio
        self.Convexidad=Convexidad
        self.Duracion=Duracion
        self.Duracion_list=Duracion_list
        self.Convexidad_list=Convexidad_list
        
        return Precio, Convexidad, Duracion, Duracion_list, Convexidad_list
        
        '''
        
        El metodo "bond_value" me permite calcular el precio, duracion y convexidad del bono. Ademas la lista de Duracion y Convexidad.
        
        Los inputs de este metodo, son:
            * lista de fechas
            * lista de fraccion de año
            * lista de flujos descontados
        
        
        Precio= sum (Flujos descontados i)
        
                     Flujo dscto i
        Duracion =  -------------- x Ti
                        Precio
        
                       Flujo dscto i
        Convexidad =  -------------- x (Ti)^2
                          Precio
        
        
        Los returns son:
            * lista de duracion
            * lista de convexidad
            * valor del precio
            * valor de la duracion (es la suma de la lista duracion)
            * valor de la convexidad (es la suma de la lista convexidad)
            
        '''
    

    
def main():
    Haircut= 95                                                                     # es el haircut del bono
    Amortizaciones=6                                                                # cantidad de amortizaciones que se quiere hacer
    cupon= 6                                                                        # es la tasa del cupon
    capitalizacion=2                                                                # la capitalización es anual=1 y semi-anual=2
    YTM= 12                                                                         # es la YTM que se desea utilizar
    
    
    F_Liquidacion=datetime.datetime.strptime('13/05/2020','%d/%m/%Y')               #Definiendo la fecha de valorización
    F_Vencimiento=datetime.datetime.strptime('15/11/2036','%d/%m/%Y')               #Definiendo la fecha de vencimiento
    F_dev_Cupon_inicial=datetime.datetime.strptime('15/11/2022','%d/%m/%Y')         #Definiendo la fecha de dev de los pagos
    F_pago_Cupon_inicial=datetime.datetime.strptime('15/11/2023','%d/%m/%Y')        #Definiendo la fecha de pago del primer cupon
    
    df1 = pd.DataFrame({'Fecha' : ['15/11/2022', '15/11/2023', '15/11/2025', '15/11/2027'], #es la matriz de los cupones step-up
                        'Cupon' : [0.5, 1.5, 2.75, 3.875]})
    
    BV = Bond_valuator(
                 HC = Haircut,
                 amort = Amortizaciones,
                 cup = cupon,
                 cap = capitalizacion,
                 ytm = YTM,
                 F_Liqui = F_Liquidacion,
                 F_Venc = F_Vencimiento,
                 F_dev_CI = F_dev_Cupon_inicial,
                 F_pago_CI = F_pago_Cupon_inicial)
    
    Fechas, year_frac = BV.dates()
    Cupon, Principal = BV.cup_and_prin(df1)
    Flujo, Flujo_dscto = BV.flujos()
    Price, Convexidad, Duracion, Duracion_list, Convexidad_list = BV.bond_values()             
    
    

    Cronograma=pd.DataFrame([Fechas,Cupon,Principal,Flujo,Flujo_dscto,Duracion_list,Convexidad_list]).T
    Cronograma.columns=['Fechas','Cupones','Principal','Flujo','Flujo_dscto','Duracion','Convexidad']
    Cronograma=Cronograma.set_index('Fechas')
    
    display(df1)
    print("\n")
    display(Cronograma)
    
    
    print(f"\nPrecio del bono para la YTM={YTM} es: usd/"+str(Price))
    print(f"\nLa Convexidad es:"+str(Convexidad))
    print(f"\nLa Duration es:"+str(Duracion))

if __name__ == '__main__':
    main()    
    
    