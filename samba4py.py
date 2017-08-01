#!/usr/bin/python
#_*_ encoding: utf-8 _*_

import subprocess
import sys
import fileinput

def execProcess(command):
    """Executa um processo.

    Essa função recebe um comando no formato de uma string,
    e o executa no S.O. Caso ele seje validado, grava a saída
    em um arquivo de log e exibe no terminal do usuário em
    tempo real.
    """
    p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
    while True:
        out = p.stderr.read(1)
        log = open('samba4py.log', 'a')
        if out == '' and p.poll() != None:
            break
        if out != '':
            sys.stdout.write(out)
            log.write(out)
            sys.stdout.flush()
        log.close()

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

with open('samba4py.log', 'ab') as log:
    log.write("01 - ATUALIZANDO O SISTEMA ...\n")
    log.close()

print "*******************************************************************"
print "******************** ATUALIZANDO O SISTEMA ... ********************"
print "*******************************************************************\n"

execProcess("apt-get update ; apt-get upgrade -y")

execProcess("clear")

with open('samba4py.log', 'ab') as log:
    log.write("02 - PREPARANDO REQUIRIMENTOS E INSTALANDO PACOTES ...\n")
    log.close()

print "*******************************************************************"
print "******** PREPARANDO REQUIRIMENTOS E INSTALANDO PACOTES ... ********"
print "*******************************************************************\n"

execProcess("apt-get install samba winbind acl attr ntpdate -y ; rm "
            "/etc/samba/smb.conf")

execProcess("ntpdate a.ntp.br")

for line in fileinput.FileInput("/etc/fstap", inplace=True, backup='_bak'):
    line.replace("errors=remount-ro",
                 "errors=remount-ro,acl,user_xattr,barrier=1")

execProcess("mount -o remount /")

execProcess("clear")

with open('samba4py.log', 'ab') as log:
    log.write("03 - COLETANDO INFORMAÇÕS PARA PROVISIONAMENTO ...\n")
    log.close()

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

with open('samba4py.log', 'ab') as log:
    log.write("03 - PROVISIONANDO CONTROLADOR DE DOMÍNIO PRINCIPAL ...\n")
    log.close()

print "*******************************************************************"
print "********* PROVISIONANDO CONTROLADOR DE DOMÍNIO PRINCIPAL **********"
print "*******************************************************************\n"

execProcess("samba-tool domain provision --server-role=dc "
            "--dns-backend=SAMBA_INTERNAL --realm="+realm+" "
            "--domain="+domain+" --adminpass="+password+" "
            "--option=\"interfaces=lo "+nic+"\" "
            "--option=\"bind interfaces only=yes\" --function-level=2008_R2")

with open('/etc/samba/smb.conf', 'r') as file:
    data = file.readlines()
    total = sum(1 for _ in file)
    for x in range(0, total):
        if data[x] == '[netlogon]':
            if data[x-1] == '':
                data[x-1] = '    dns forwarder = '+dns+'\n    server ' \
                                                       'services = ' \
                                                   's3fs rpc nbt wrepl ldap ' \
                                                   'cldap kdc drepl winbind ' \
                                                   'ntp_signd kcc dnsupdate ' \
                                                   'dns\n'
            else:
                data[x-1] += '\n    dns forwarder = '+dns+'\n    server ' \
                                                          'services = s3fs ' \
                                                          'rpc nbt wrepl ' \
                                                          'ldap cldap kdc ' \
                                                          'drepl winbind ' \
                                                          'ntp_signd kcc ' \
                                                          'dnsupdate dns\n'
with open('/etc/samba/smb.conf', 'w') as file:
    file.writelines(data)
    file.close()

execProcess("/etc/init.d/samba restart")

execProcess("clear")

with open('samba4py.log', 'ab') as log:
    log.write("***** SAMBA4 PROVISIONADO COM SUCESSO ! *****")
    log.close()

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
