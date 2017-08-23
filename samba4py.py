#!/usr/bin/python
#_*_ encoding: utf-8 _*_

import subprocess
import sys
import logging

logging.basicConfig(filename='samba4py.log',level=logging.DEBUG)

root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)
       
        
def execProcess(command):
    process = subprocess.Popen(command, shell=True, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.STDOUT)

    while True:
        nextline = process.stdout.readline()
        if nextline == '' and process.poll() is not None:
            break
        sys.stdout.write(nextline)
        sys.stdout.flush()

    output = process.communicate()[0]
    exitCode = process.returncode

    if (exitCode == 0):
        return output
    else:
        raise ProcessException(command, exitCode, output)
    

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

logging.info('01 - ATUALIZANDO O SISTEMA ...\n')

print "*******************************************************************"
print "******************** ATUALIZANDO O SISTEMA ... ********************"
print "*******************************************************************\n"

execProcess("apt-get update ; apt-get upgrade -y")

execProcess("clear")

logging.info('02 - PREPARANDO REQUIRIMENTOS E INSTALANDO PACOTES ...\n')

print "*******************************************************************"
print "******** PREPARANDO REQUIRIMENTOS E INSTALANDO PACOTES ... ********"
print "*******************************************************************\n"

execProcess("apt-get install samba winbind acl attr ntpdate -y ; "
            "rm /etc/samba/smb.conf")

execProcess("ntpdate a.ntp.br")

#Adiciona funcionalidades necessárias no arquivo "/etc/fstab" para receber o
#provisionamento, e remonta a partição raiz "/"
logging.info('02.1 - PREPARANDO E REMONTANDO A PARTIÇÃO RAIZ ...')

f = open('/etc/fstab', 'r')
tempstr = f.read()
f.close()
tempstr = tempstr.replace("errors=remount-ro","errors=remount-ro,acl,"
                                              "user_xattr,barrier=1")
fout = open('/etc/fstab', 'w')
fout.write(tempstr)
fout.close()

execProcess("mount -o remount /")

execProcess("clear")

logging.info('02.2 - PARTIÇÃO RAIZ PREPARADA E REMONTADA.')
#Fim

logging.info('03 - COLETANDO INFORMAÇÕS PARA PROVISIONAMENTO ...\n')

print "*******************************************************************"
print "********* PREENCHA AS INFORMAÇÕES A SEGUIR PARA CONTINUAR *********"
print "*******************************************************************\n"

nic = raw_input("Digite o nome da placa de rede a ser usada (ex: eth0): ")
dns = raw_input("Digite um DNS que será usado para consultas externas "
                "(ex: 8.8.8.8): ")
realm = raw_input("Digite o nome FQDN de domínio a ser usado "
                  "(ex: exemplo.com): ")
domain = raw_input("Digite o nome curto do domínio (ex: exemplo): ")
password = raw_input('Crie a senha do usuário "Administrator" do Domínio, \n'
                     'contendo letras, números e caracteres especias '
                     '(ex: Passw0rd): ')

execProcess("clear")

logging.info('03 - PROVISIONANDO CONTROLADOR DE DOMÍNIO PRINCIPAL ...\n')

print "*******************************************************************"
print "********* PROVISIONANDO CONTROLADOR DE DOMÍNIO PRINCIPAL **********"
print "*******************************************************************\n"

execProcess("samba-tool domain provision --server-role=dc "
            "--dns-backend=SAMBA_INTERNAL --realm="+realm+" "
            "--domain="+domain+" --adminpass="+password+" "
            "--option=\"interfaces=lo "+nic+"\" "
            "--option=\"bind interfaces only=yes\" --function-level=2008_R2")

# Prepara o smb.conf para usar todos os recursos necessários para o servidor
# funcionar corretamente, já que o mesmo possui opções a mais que as default
logging.info('03.1 - PREPARANDO O ARQUIVO SMB.CONF ...')

f = open('/etc/samba/smb.conf', "r")
contents = f.readlines()
f.close()

contents[8] = '        dns forwarder = '+dns+'\n'
contents[9] = '        server services = s3fs rpc nbt wrepl ldap cldap kdc ' \
              'drepl winbind ntp_signd kcc dnsupdate dns\n\n'

f = open('/etc/samba/smb.conf', "w")
f.writelines(contents)
f.close()

logging.info('03.2 - Arquivo smb.conf preparado com sucesso.')
# Fim

logging.info('03.3 - Instalando arquivo krb5.conf no sistema ...')
execProcess("cp /var/lib/samba/private/krb5.conf /etc/")

logging.info('03.4 - Reiniciando os processos samba ...')
execProcess("/etc/init.d/samba restart")

execProcess("clear")

logging.info('***** SAMBA4 PROVISIONADO COM SUCESSO ! *****\n')

print "*******************************************************************"
print "*************** SAMBA4 PROVISIONADO COM SUCESSO ! *****************"
print "*******************************************************************"
print "******* COLOQUE ESTAÇÕES DE TRABALHO NO DOMÍNIO USANDO ************"
print "******* AS SEGUINTES INFORMAÇÕES: **************************"
print "*******************************************************************"
print "*******************************************************************"
print "DOMÍNIO: "+realm
print "ADMINISTRADOR DO DOMÍNIO: Administrator@"+realm
print "SENHA: "+password
print "*******************************************************************"
print "*******************************************************************\n"
