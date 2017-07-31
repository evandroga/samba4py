#!/usr/bin/python
#_*_ encoding: utf-8 _*_

import subprocess
import sys

def execProcess(command):
    p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
    while True:
        out = p.stderr.read(1)
        if out == '' and p.poll() != None:
            break
        if out != '':
            sys.stdout.write(out)
            sys.stdout.flush()

print "*******************************************************************"
print "*******************************************************************"
print "*************** SAMBA4PY - Vr. 1.0, BY EVANDRO GOMES***************"
print "*******************************************************************"
print "*******************************************************************"
print "****** ESTE SCRIPT AUTOMATIZA A INSTALAÇÃO E PROVISIONAMENTO ******"
print "***** DO PACOTE SAMBA4 COMO CONTROLADOR DE DOMÍNIOS PRINCIPAL *****"
print "*******************************************************************"
print "*******************************************************************"
print "****** ANTES DE PROSSEGUIR, TENHA CERTEZA DE TER CONFIGURADO: *****"
print "****** UM HOSTNAME VÁLIDO NO PADRÃO FQDN; *************************"
print "****** SERVIDOR DNS PRIMÁRIO EM LOOPBACK (127.0.0.1); *************"
print "****** UM ENDEREÇO IP FIXO NA PLACA DE REDE A SER USADA. **********"
print "*******************************************************************"
print "*******************************************************************\n"

raw_input("Digite ENTER para continuar, ou Ctrl+C para cancelar ...")
execProcess("clear")

print "*******************************************************************"
print "******************** ATUALIZANDO O SISTEMA ... ********************"
print "*******************************************************************\n"

execProcess("apt-get update ; apt-get upgrade -y")
execProcess("clear")

print "*******************************************************************"
print "******** PREPARANDO REQUIRIMENTOS E INSTALANDO PACOTES ... ********"
print "*******************************************************************\n"

execProcess("apt-get install samba winbind acl attr ntpdate ; rm /etc/samba/smb.conf")
execProcess("ntpdate a.ntp.br")
execProcess("clear")

print "*******************************************************************"
print "********* PREENCHA AS INFORMAÇÕES A SEGUIR PARA CONTINUAR *********"
print "*******************************************************************\n"

nic = raw_input("Digite o nome da placa de rede a ser usada (ex: eth0): ")
dns = raw_input("Digite um DNS que será usado para consultas externas (ex: 8.8.8.8): ")
realm = raw_input("Digite o nome FQDN de domínio a ser usado (ex: exemplo.com): ")
domain = raw_input("Digite o nome curto do domínio (ex: exemplo): ")
password = raw_input('Crie a senha do usuário "Administrator" do Domínio, \n'
                     'contendo letras, números e caracteres especias (ex: Passw0rd): ')
execProcess("clear")

print "*******************************************************************"
print "********* PROVISIONANDO CONTROLODAR DE DOMÍNIO PRINCIPAL **********"
print "*******************************************************************\n"

execProcess("samba-tool domain provision --server-role=dc --dns-backend=SAMBA_INTERNAL --realm="+realm+" --domain="+domain+" --adminpass="+password+" --option=\"interfaces=lo "+nic+"\" --option=\"bind interfaces only=yes\"")
execProcess("clear")

print "*******************************************************************"
print "*************** SAMBA4 PROVISIONADO COM SUCESSO ! *****************"
print "*******************************************************************"
print "******* COLOQUE ESTAÇÕES DE TRABALHO NO DOMÍNIO USANDO ************"
print "******* USANDO AS SEGUINTES INFORMAÇÕES: **************************"
print "*******************************************************************"
print "*******************************************************************"
print "DOMÍNIO: "+realm
print "ADMINISTRADOR DO DOMÍNIO: Administrator@"+realm
print "SENHA: "+password
print "*******************************************************************"
print "*******************************************************************\n"
