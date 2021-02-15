# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 14:43:13 2020

@author: Emanuel
"""



import pandas as pd #pandas es una libreria que permite trabajar con datos
import datetime #libreria para manejo de fechas
import numpy as np #libreria para operaciones con matrices, polinomios, entre otros 
from dateutil.relativedelta import relativedelta #funcion para poder realizar operaciones con fechas



class BulletBond:
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

    def cup_and_prin(self):
        
        Cupon=[self.cup/self.cap]*len(self.Fechas)
        Principal=[0]*len(self.Fechas)  
        new_list=[0]*len(self.Fechas) 
                
        #-----creo la lista de los principales---------------------
        Amort=self.amort
        j=0
        while j < Amort:
            new_list[2*j] = self.HC/self.amort
            j=j+1
        
        Principal=new_list[::-1]
        
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
        self.cup_and_prin()

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
        
        Precio=np.round(np.sum(self.Flujo_dscto),3)

        #-------Calculando Duration y Convexidad del bono------------------
        
        for i in range(0,len(self.Fechas)):
            Duracion_list.append(np.round((self.Flujo_dscto[i]/Precio)*self.year_frac[i],3))
            Convexidad_list.append(np.round((self.Flujo_dscto[i]/Precio)*np.power(self.year_frac[i],2),3))
              
            
        Duracion=np.round(np.sum(Duracion_list)/(1+(self.ytm/100/self.cap)),3)
        Convexidad=np.round(np.sum(Convexidad_list),3)                          # Hago la suma de la lista de Convexidad para mostrar el valor final
        
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
    Haircut= 100                                                                    # es el haircut del bono
    Amortizaciones=1                                                                # cantidad de amortizaciones que se quiere hacer
    cupon= 6                                                                        # es la tasa del cupon
    capitalizacion=2                                                                # la capitalización es anual=1 y semi-anual=2
    YTM= 10                                                                          # es la YTM que se desea utilizar
    
    
    F_Liquidacion=datetime.datetime.strptime('28/07/2020','%d/%m/%Y')               #Definiendo la fecha de valorización
    F_Vencimiento=datetime.datetime.strptime('26/07/2030','%d/%m/%Y')               #Definiendo la fecha de vencimiento
    F_dev_Cupon_inicial=datetime.datetime.strptime('28/07/2020','%d/%m/%Y')         #Definiendo la fecha de dev de los pagos
    F_pago_Cupon_inicial=datetime.datetime.strptime('28/01/2021','%d/%m/%Y')        #Definiendo la fecha de pago del primer cupon

    
    BP = BulletBond(
                 HC = Haircut,
                 amort = Amortizaciones,
                 cup = cupon,
                 cap = capitalizacion,
                 ytm = YTM,
                 F_Liqui = F_Liquidacion,
                 F_Venc = F_Vencimiento,
                 F_dev_CI = F_dev_Cupon_inicial,
                 F_pago_CI = F_pago_Cupon_inicial)
    
    
    Fechas, year_frac = BP.dates()
    Cupon, Principal = BP.cup_and_prin()
    Flujo, Flujo_dscto = BP.flujos()
    Price, Convexidad, Duracion, Duracion_list, Convexidad_list = BP.bond_values()             

    

    Cronograma=pd.DataFrame([Fechas,Cupon,Principal,Flujo,Flujo_dscto,Duracion_list,Convexidad_list]).T
    Cronograma.columns=['Fechas','Cupones','Principal','Flujo','Flujo_dscto','Duracion','Convexidad']
    Cronograma=Cronograma.set_index('Fechas')
    
    display(Cronograma)

    
    print(f"Precio del bono para la YTM={YTM} es: usd/"+str(Price))
    print(f"La Convexidad es:"+str(Convexidad))
    print(f"La Duration es:"+str(Duracion))

if __name__ == '__main__':
    main()    
    
    