#! /usr/bin/python3.6
#
#   ----------------------------------------------------------------------------------------------------
#   Autor: David De Maya Merras - daviddemayamerras@gmail.com - https://hardsoftsecurity.es
#   Fecha: 04-02-2019 10:41 AM.
#   Los MIB's que he utilizado para este script son:
#   https://global.download.synology.com/download/Document/MIBGuide/Synology_DiskStation_MIB_Guide.pdf
#   Este script esta hecho con la idea de monitorizar los recursos más importantes de una synology.
#   ----------------------------------------------------------------------------------------------------

from hurry.filesize import size, si
import argparse, sys
#instalar libreria hurry.filesize, argparse y pysnmp
#Declaramos los parámetros de entrada del script.
parser = argparse.ArgumentParser()
parser.add_argument("-v","--version",help="Parámetro utilizado para la versión del script.",action="store_true")
parser.add_argument("-t","--temperatura",help="Parámetro utilizado para sacar la temperatura.",action="store_true")
parser.add_argument("-s","--storagevol",help="Parámetro utilizado para el calculo de porcentaje libre de los volumenes.",action="store_true")
parser.add_argument("-S","--statusvol",help="Parámetro utilizado para ver el estado de un volumen.",action="store_true")
parser.add_argument("-C","--cpu",help="Parámetro para calcular el procentaje de uso de CPU por el sistema.",action="store_true")
parser.add_argument("-T","--hdd",help="Parámetro para comprobar el estado de los discos duros de la synology.",action="store_true")
parser.add_argument("-a","--almacenamiento",help="Parámetro para calcular el espacio de Bytes a Gigabytes.",action="store_true")
parser.add_argument("-j","--sistema",help="Parámetro para comprobar el estado del sistema.", action="store_true")
parser.add_argument("-o","--oid",help="Parámetro utilizado para el OID para monitorizar.")
parser.add_argument("-O","--OID",help="Parámetro utilizado para un segundo OID.")
args = parser.parse_args()

#Variables:
ipHost = "yourIP"
portHost = "161"
comunidadHost = "public"

#Declaración de los OID's que queremos monitorizar:
#Sistema:
oidEstSistema = ".1.3.6.1.4.1.6574.1.1.0"
oidEstVentiladores = ".1.3.6.1.4.1.6574.1.4.1.0"
oidEstVentiladorCpu = ".1.3.6.1.4.1.6574.1.4.2.0"
oidEstAlimentacion = ".1.3.6.1.4.1.6574.1.3.0"
oidTemperatura = ".1.3.6.1.4.1.6574.1.2.0"
oidCpu = "1.3.6.1.4.1.2021.11.9.0"
oidNombreDiscos = ".1.3.6.1.4.1.6574.2.1.1.2"
oidEstatusDiscos = ".1.3.6.1.4.1.6574.2.1.1.5"

#Función comprobación estado del sistema:
def comprobacionSistema(estado):
    if estado == 2:
        return 2
    elif estado == 1:
        return 1

#Función para que se reutilice el código de consulta SNMP.
def snmpget(ip,comunidad,oid):
 
  from pysnmp.entity.rfc3413.oneliner import cmdgen
  #Establecemos la recogida de argumentos al llamar la funcion.
  SNMP_HOST = ip
  SNMP_PORT = portHost
  SNMP_COMMUNITY = comunidad
 
  cmdGen = cmdgen.CommandGenerator()
  #Aqui realizamos la consulta snmp y el resultado lo igualamos a las variables: 
  errorIndication, errorStatus, errorIndex, varBinds = cmdGen.getCmd(
    cmdgen.CommunityData(SNMP_COMMUNITY),
    cmdgen.UdpTransportTarget((SNMP_HOST, SNMP_PORT)),
    oid
  )

  #Comprobamos si existen errores al realizar la consulta SNMP.
  if errorIndication:
    print(errorIndication)
  else:
    if errorStatus:
      print('%s at %s' % (
        errorStatus.prettyPrint(),
        errorIndex and varBinds[int(errorIndex)-1] or '?'
       )
     )
    else:
      for name, val in varBinds:
        return val

#Función que calcula el porcentaje que representa numeroUso de numeroTotal.
def porcentajeLibre(numeroUso,numeroTotal):
    numeroPorcentaje = (numeroUso * 100) / numeroTotal
    return numeroPorcentaje

#Comenzamos el script principal.
if __name__ == '__main__':
    if args.version:
        print("Versión del script 0.1 - script utilizado para la monitorización de Synology RX-415")

    #Comprobación de la temperatura:
    elif args.temperatura:
        temperaturaSynology = snmpget(ipHost,comunidadHost,oidTemperatura)
        strTemperaturaSynology = str(temperaturaSynology)
        
        if int(temperaturaSynology) >= 60:
            respuesta = "CRITICAL: " + strTemperaturaSynology
            print(respuesta)
            sys.exit(2)
        elif int(temperaturaSynology) >= 50:
            respuesta = "WARNING: " + strTemperaturaSynology
            print(respuesta)
            sys.exit(1)
        else:
            respuesta = "Temperatura correcta - OK: " + strTemperaturaSynology + " grados."
            print(respuesta)
            sys.exit(0)

    #Comprobación del porcentaje de espacio libre de los volumenes de la synology:
    elif args.storagevol:
        espacioUsado = snmpget(ipHost,comunidadHost,args.oid)
        espacioTotal = snmpget(ipHost,comunidadHost,args.OID)
        resultadoPorcentaje = porcentajeLibre(espacioUsado,espacioTotal)

        numeroCompleto = str(resultadoPorcentaje).split(".")
        numero = numeroCompleto[0]

        if int(numero) <= 5:
            respuesta = "CRITICAL! queda libre un " + numero + "%" + " de almacenamiento."
            print(respuesta)
            sys.exit(2)
        elif int(numero) <= 8:
            respuesta = "WARNING! queda libre un " + numero + "%" + " de almacenamiento."
            print(respuesta)
            sys.exit(1)
        else:
            respuesta = "El espacio libre disponible es un " + numero + "%."
            print(respuesta)
            sys.exit(0)

    #Paso de Bytes a Gigabytes del espacio de los volumenes de la synology:
    elif args.almacenamiento:
        tamañoLibre = snmpget(ipHost,comunidadHost,args.oid)
        tamañoLibre = tamañoLibre / 1024
        tamañoLibre = tamañoLibre / 1024
        tamañoLibre = tamañoLibre / 1024
        tamañoLibreFinal = str(tamañoLibre).split(".")
        resultado = "Quedan libres: " + tamañoLibreFinal[0] + " Gb de 16TB."
        print(resultado)
        sys.exit(0)

    #Comprobación del estado de los volumenes:
    elif args.statusvol:
        statusVolumen = snmpget(ipHost,comunidadHost,args.oid)
        statusVolumenStr = str(statusVolumen)

        if statusVolumen == 1:
            respuesta = "El estado del volumen es: CORRECTO - OK! estado: " + statusVolumenStr
            print(respuesta)
            sys.exit(0)
        elif int(statusVolumen) == 11:
            respuesta = "El estado del volumen es: DEGRADADO! estado: " + statusVolumenStr
            print(respuesta)
            sys.exit(2)
        elif int(statusVolumen) == 12:
            respuesta = "El estado del volumen es: ROTO! estado: " + statusVolumenStr
            print(respuesta)
            sys.exit(2)
        else:
            respuesta = "Consultar tabla de estados de volumen, el volumen es: " + statusVolumenStr
            print(respuesta)
            sys.exit(2)

    #Comprobación de la CPU:
    elif args.cpu:
        porcentajeCpu = snmpget(ipHost,comunidadHost,oidCpu)
        porcentajeCpuStr = str(porcentajeCpu)

        if porcentajeCpu >= 90:
            respuesta = "El estado de la CPU es CRITICAL! porcentaje: " + porcentajeCpuStr
            print(respuesta)
            sys.exit(2)
        elif porcentajeCpu >= 80:
            respuesta = "El estado de la CPU es WARNING! porcentaje: " + porcentajeCpuStr
            sys.exit(1)
        elif porcentajeCpu <= 79:
            respuesta = "El estado de la CPU es OK! porcentaje: " + porcentajeCpuStr
            print(respuesta)
            sys.exit(0)
        else:
            respuesta = "Comprobar estado: " + porcentajeCpuStr

    #Comprobación del estado de los discos duros:
    elif args.hdd:
        i = 0
        #Inicializamos los arrays.
        discosDurosCorrectos = []
        discosDurosParticion = []
        discosDurosRotos = []
        discosDurosElse = []
        #Creamos un for con un rango de 8, que son los discos que tiene la synology.
        for i in range(8):
            #por cada disco, sacamos el oid de del estado y su nombre.
            oidNombre = oidNombreDiscos + "." + str(i)
            nombreDiscosDuros = snmpget(ipHost,comunidadHost,oidNombre)
            oidStatus = oidEstatusDiscos + "." + str(i)
            statusDiscosDuros = snmpget(ipHost,comunidadHost,oidStatus)
            #Comprobamos el estado de los discos y guardamos el nombre del disco duro en su array correspondiente.
            if statusDiscosDuros == 1:
                discosDurosCorrectos.append(str(nombreDiscosDuros))
            elif statusDiscosDuros == 4:
                discosDurosParticion.append(str(nombreDiscosDuros))
            elif statusDiscosDuros == 5:
                discosDurosRotos.append(str(nombreDiscosDuros))
            else:
                discosDurosElse.append(str(nombreDiscosDuros))
        #Contamos cuantos discos hay en cada array.
        contadorCorrectos = len(discosDurosCorrectos)
        contadorRotos = len(discosDurosRotos)
        contadorParticion = len(discosDurosParticion)
        contadorElse = len(discosDurosElse)
        #Comprobamos si existen discos duros rotos o en otro estado y los guardamos en su variable correspondiente.
        if contadorRotos > 0:
            hddRotos = ""
            for discoDuro in discosDurosRotos:
                hddRotos += discoDuro + ", "
        elif contadorElse > 0:
            hddElse = ""
            for discoDuro in discosDurosRotos:
                hddElse += discoDuro
        elif contadorParticion > 0:
            hddParticion = ""
            for discoDuro in discosDurosRotos:
                hddParticion += discoDuro
        else:
            hddCorrectos = ""
            for discoDuro in discosDurosCorrectos:
                hddCorrectos += discoDuro + ", "

        if (contadorRotos or contadorElse or contadorParticion) > 0:
            respuesta = "Los discos: estan rotos, " + hddRotos + "los discos: " + hddElse + "se encuentran en un estado diferente, los discos: " + hddParticion + "tienen la particion corrompida."
            print(respuesta)
            sys.exit(2)
        elif contadorCorrectos > 0:
            respuesta = "Los discos: " + hddCorrectos + "se ecuentran OK!"
            print(respuesta)
            sys.exit(0)
        else:
            print("Revisar")
            sys.exit(1)

    #Comprobación del estado del sistema:
    elif args.sistema:
        estadoDelSistema = snmpget(ipHost,comunidadHost,oidEstSistema)
        estadoDeVentiladores = snmpget(ipHost,comunidadHost,oidEstVentiladores)
        estadoVentiladoresCpu = snmpget(ipHost,comunidadHost,oidEstVentiladorCpu)
        estadoAlimentacion = snmpget(ipHost,comunidadHost,oidEstAlimentacion)

        rEstadoDelSistema = comprobacionSistema(estadoDelSistema)
        rEstadoDeVentiladores = comprobacionSistema(estadoDeVentiladores)
        rEstadoDeVentiladoresCpu = comprobacionSistema(estadoVentiladoresCpu)
        rEstadoAlimentacion = comprobacionSistema(estadoAlimentacion)

        if rEstadoAlimentacion and rEstadoDelSistema and rEstadoDeVentiladores and rEstadoDeVentiladoresCpu == 1:
            respuesta = "El estado del sistema es correcto - OK"
            print(respuesta)
            sys.exit(0)
        else:
            respuesta = ("ERROR: Estado del sistema = " + str(rEstadoDelSistema) + " Estado de los ventiladores = " + 
            str(rEstadoDeVentiladores) + " Estado del ventilador de la CPU = " + str(rEstadoDeVentiladoresCpu) + " Estado de la alimentacion = " + str(rEstadoAlimentacion))
            print(respuesta)
            sys.exit(2)
    #Si no se introduce ningún parámetro:
    else:
        respuesta = "No ha introducido ningún parámetro, por favor para más información utilice -h o --help"
        print(respuesta)
        sys.exit(3)