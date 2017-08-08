#!/usr/bin/python
#_*_ encoding: utf-8 _*_

import subprocess
import sys
import logging

"""
def execProcess(command_line):
    command_line_args = shlex.split(command_line)

    logging.info('Subprocess: "' + command_line + '"')

    try:
        command_line_process = subprocess.Popen(
            command_line_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        process_output, _ =  command_line_process.communicate()

        # process_output is now a string, not a file,
        # you may want to do:
        # process_output = StringIO(process_output)
        logging.info(process_output)
    except (OSError, subprocess.CalledProcessError) as exception:
        logging.info('Exception occured: ' + str(exception))
        logging.info('Subprocess failed')
        return False
    else:
        # no exception was raised
        logging.info('Subprocess finished')

    return True
"""

def execProcess(command):
    """Executa um processo.

    Essa função recebe um comando no formato de uma string,
    e o executa no S.O. Caso ele seje validado, grava a saída
    em um arquivo de log e exibe no terminal do usuário em
    tempo real.
    """
    try:
        p = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
        while True:
            out = p.stderr.read(1)
            if out == '' and p.poll() != None:
                break
            if out != '':
                logging.info(out)
                sys.stdout.write(out)
                sys.stdout.flush()        
    except (OSError, subprocess.CalledProcessError) as exception:
        logging.info('Exception occured: ' + str(exception))
        logging.info('Subprocess failed')
    else:
        # no exception was raised
        logging.info('Subprocess finished')
    

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

execProcess("apt-get install samba winbind acl attr ntpdate -y ; "
            "rm /etc/samba/smb.conf")

execProcess("ntpdate a.ntp.br")

#Adiciona funcionalidades necessárias no arquivo "/etc/fstab" para receber o
#provisionamento, e remonta a partição raiz "/"
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
#Fim

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

f = open('/etc/samba/smb.conf', "r")
contents = f.readlines()
f.close()

contents[8] = '        dns forwarder = '+dns+'\n'
contents[9] = '        server services = s3fs rpc nbt wrepl ldap cldap kdc ' \
              'drepl winbind ntp_signd kcc dnsupdate dns\n'

f = open('/etc/samba/smb.conf', "w")
f.writelines(contents)
f.close()

execProcess("cp /var/lib/samba/private/krb5.conf /etc/")

execProcess("/etc/init.d/samba restart")

execProcess("clear")

with open('samba4py.log', 'ab') as log:
    log.write("\n***** SAMBA4 PROVISIONADO COM SUCESSO ! *****\n")
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
