#!/usr/bin/python
#_*_ encoding: utf-8 _*_

import subprocess
import sys
import logging


#Prepara as configurações necessárias para quardar informações
#em um arquivo de logg chamado 'samba4py.log', presente no
#diretório raiz do script.

formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='samba4py.log', 
                   level=logging.DEBUG,
                   format=formatter)


def checkPackage(package, running=False):
    '''Busca por um processo rodando
    
    Função que busca se um pacote está instalado no sistema e
    retorna true (verdadeiro) caso esteja. Ou busca se o pacote
    está rodando no sistema. 
    
    '''
    if running:
        process = subprocess.Popen(('ps', 'aux'), stdout=subprocess.PIPE)
        output = process.communicate()[0]
        for line in output.split('\n'):
            if package in line:
                return true
    else:
        process = subprocess.Popen(('dpkg-query', '-f',
                                   '\'${binary:Package}\n\'', '-W'), 
                                   stdout=subprocess.PIPE)
        output = process.communicate()[0]
        for line in output.split('\n'):
            if package in line:
                return true


def execProcess(command):
    '''Executa um processo externo
    
    Função que chama um processo externo, mostra a saída
    no terminal em tempo de execução e guarda a mesma 
    em arquivo de logg presente no diritório do script.
    
    '''
    process = subprocess.Popen(command, shell=True, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.STDOUT)
    while True:
        nextline = process.stdout.readline()
        if nextline == '' and process.poll() is not None:
            break
        sys.stdout.write(nextline)
        logging.info(nextline)
        sys.stdout.flush()
    output = process.communicate()[0]
    exitCode = process.returncode
    if (exitCode == 0):
        return output
    else:
        logging.warning('Ocorreu uma exceção e o script foi interrompido.')
        raise Exception(command, exitCode, output)
    

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

logging.info('01 - VERIFICANDO SE O SAMBA 4 JÁ EXISTE NO SISTEMA ...\n')

if checkPackage('samba'):
    process = subprocess.Popen(('smbclient',
                                '-L',
                                'localhost',
                                '-U%',
                                '|',
                                'grep',
                                'netlogon'), stdout=subprocess.PIPE)
    exitCode = process.returncode
    if (exitCode == 0):
        print "Parece que o Samba 4 já está instalado e provisionado."
        print "O script samba4py não poderá continuar. Se quiser um"
        print "novo provisionamento, limpe ou desinstale o samba 4.\n"
        raw_input("Digite qualquer telca ou Ctrl+C para sair ...")
        sys.exit(1)

logging.info('01.1 - COLETANDO INFORMAÇÕS NECESSÁRIAS ...\n')

print "*******************************************************************"
print "********* PREENCHA AS INFORMAÇÕES A SEGUIR PARA CONTINUAR *********"
print "*******************************************************************\n"

#Coleta as informações necessárias para iniciar o provisionamento do samba4

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

logging.info('02 - ATUALIZANDO O SISTEMA ...\n')

print "*******************************************************************"
print "******************** ATUALIZANDO O SISTEMA ... ********************"
print "*******************************************************************\n"

execProcess("apt-get update && apt-get upgrade -y")

execProcess("clear")

logging.info('03 - PREPARANDO REQUIRIMENTOS E INSTALANDO PACOTES ...\n')

print "*******************************************************************"
print "******** PREPARANDO REQUIRIMENTOS E INSTALANDO PACOTES ... ********"
print "*******************************************************************\n"

pacotes = ['samba', 'winbind', 'acl', 'attr', 'ntpdate']
for p in pacotes:
    if not checkPackage(p):
        execProcess("apt-get install "+p+" -y")

execProcess("rm -f /etc/samba/smb.conf")

execProcess("ntpdate a.ntp.br")

#Adiciona funcionalidades necessárias no arquivo "/etc/fstab" para receber o
#provisionamento, e remonta a partição raiz "/"

logging.info('03.1 - PREPARANDO E REMONTANDO A PARTIÇÃO RAIZ ...')
f = open('/etc/fstab', 'r')
tempstr = f.read()
f.close()
if not 'errors=remount-ro,acl,user_xattr,barrier=1' in tempstr:
    tempstr = tempstr.replace("errors=remount-ro","errors=remount-ro,acl,"
                                                  "user_xattr,barrier=1")
fout = open('/etc/fstab', 'w')
fout.write(tempstr)
fout.close()

execProcess("mount -o remount /")

execProcess("clear")

logging.info('03.2 - PARTIÇÃO RAIZ PREPARADA E REMONTADA.')

logging.info('04 - PROVISIONANDO CONTROLADOR DE DOMÍNIO PRINCIPAL ...\n')

print "*******************************************************************"
print "********* PROVISIONANDO CONTROLADOR DE DOMÍNIO PRINCIPAL **********"
print "*******************************************************************\n"

#Realiza os comandos de provisionamento do samba4 com opções extras
#de limitar a saída do servidor apenas pela placa de rede especificada

execProcess("samba-tool domain provision --server-role=dc "
            "--dns-backend=SAMBA_INTERNAL --realm="+realm+" "
            "--domain="+domain+" --adminpass="+password+" "
            "--option=\"interfaces=lo "+nic+"\" "
            "--option=\"bind interfaces only=yes\" --function-level=2008_R2")

#Prepara o smb.conf para usar todos os recursos necessários para o servidor
#funcionar corretamente, já que o mesmo possui opções a mais que as default

logging.info('04.1 - PREPARANDO O ARQUIVO SMB.CONF ...')

f = open('/etc/samba/smb.conf', "r")
contents = f.readlines()
f.close()
contents[8] = '        dns forwarder = '+dns+'\n'
contents[9] = '        server services = s3fs rpc nbt wrepl ldap cldap kdc ' \
              'drepl winbind ntp_signd kcc dnsupdate dns\n\n'
f = open('/etc/samba/smb.conf', "w")
f.writelines(contents)
f.close()

logging.info('04.2 - Arquivo smb.conf preparado com sucesso.')

#Instala o arquivo 'krb5.conf' gerado pelo provisionamento do samba4
#no diretorio '/etc' do sistema.

logging.info('04.3 - Instalando arquivo krb5.conf no sistema ...')

execProcess("cp /var/lib/samba/private/krb5.conf /etc/")

#Reinicia os processos do samba4

logging.info('04.4 - Reiniciando os processos samba ...')

execProcess("/etc/init.d/samba restart")

execProcess("clear")

logging.info('***** SAMBA4 PROVISIONADO COM SUCESSO ! *****\n')

print "*******************************************************************"
print "*************** SAMBA4 PROVISIONADO COM SUCESSO ! *****************"
print "*******************************************************************"
print "******* COLOQUE ESTAÇÕES DE TRABALHO NO DOMÍNIO USANDO ************"
print "******* AS SEGUINTES INFORMAÇÕES: *********************************"
print "*******************************************************************"
print "*******************************************************************"
print "DOMÍNIO: "+realm
print "ADMINISTRADOR DO DOMÍNIO: Administrator@"+realm
print "SENHA: "+password
print "*******************************************************************"
print "*******************************************************************\n"
