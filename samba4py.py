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
    depois pesquisa se o mesmo está rodando, retornando True
    (Verdadeiro) caso esteja. Se apenas precisar saber se um
    pacote está instalado, basta suprimir o argumento "running".
    
    '''
    if running:
        p1 = subprocess.Popen(('dpkg-query', '-f',
                                   '\'${binary:Package}\n\'', '-W'), 
                                   stdout=subprocess.PIPE)
        o1 = p1.communicate()[0]
        for line in o1.split('\n'):
            if package in line:
                p2 = subprocess.Popen(('ps', 'aux'), 
                                      stdout=subprocess.PIPE)
                o2 = p2.communicate()[0]
                for line in o2.split('\n'):
                    if package in line:
                        return True
    else:
        process = subprocess.Popen(('dpkg-query', '-f',
                                   '\'${binary:Package}\n\'', '-W'), 
                                   stdout=subprocess.PIPE)
        output = process.communicate()[0]
        for line in output.split('\n'):
            if package in line:
                return True


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

#Antes de mais nada, é feita uma busca pelo sistema se o pacote samba 4 já está
#instalado. Caso esteja, é feito um teste simples para saber se já está provi-
#sionado como DC e se estiver aborta a execução do script.

print "*******************************************************************"
print "*** CONFERINDO SE SAMBA 4 JÁ ESTÁ INSTALADO E PROVISIONADO ... ****"
print "*******************************************************************\n"

if checkPackage('samba'):
    if not checkPackage('smbclient'):
        execProcess("apt-get install smbclient -y")
    process = subprocess.Popen(('smbclient', 
                               '-L', 
                               'localhost', 
                               '-U%'), stdout=subprocess.PIPE)
    out = process.communicate()[0]
    for line in out.split('\n'):
        if 'netlogon' in line:
            execProcess("clear")
            print "********************************************************" \
                  "***********"
            print "********************************************************" \
                  "***********"
            print "****** Parece que o Samba 4 já está instalado e " \
                  "provisionado. *****"
            print "************** O script samba4py não poderá continuar. " \
                  "************"
            print "*** Para um novoprovisionamento, limpe ou desinstale o " \
                  "samba 4. ***"
            print "********************************************************" \
                  "***********"
            print "********************************************************" \
                  "***********\n"
            raw_input("Pressione qualquer tecla para sair ...")
            sys.exit(1)

execProcess("clear")

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

#Verifica e atualiza, se necessário, os pacotes do sistema antes de continuar.

print "*******************************************************************"
print "******************** ATUALIZANDO O SISTEMA ... ********************"
print "*******************************************************************\n"

execProcess("apt-get update && apt-get upgrade -y")

execProcess("clear")

#Instala o samba4 e demais pacotes necessários para o provisionamento, bem
#como sicroniza a hora local com uma hora de internet, de acordo a NTP Brasil.

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

with open('/etc/fstab', 'r+') as f:
    tempstr = f.read()
    if not 'errors=remount-ro,acl,user_xattr,barrier=1' in tempstr:
        tempstr = tempstr.replace("errors=remount-ro","errors=remount-ro,acl,"
                                                      "user_xattr,barrier=1")      
    f.write(tempstr)
    f.close()

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

with open('/etc/samba/smb.conf', "r+") as f:        
    contents = f.readlines()
    contents[8] = '        dns forwarder = {0}\n'.format(dns)
    contents[9] = '        server services = s3fs rpc nbt wrepl ldap' \
                  ' cldap kdc drepl winbind ntp_signd kcc dnsupdate ' \
                  'dns\n\n'
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
