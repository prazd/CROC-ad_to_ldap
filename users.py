#!/usr/bin/python
#coding: utf-8

import ldap, re, os, time, getpass
import ldap.modlist as modlist


User = getpass.getuser()
AD_Server = ''
AD_BaseDN = ''
AD_UserFilter = '(objectClass=user)'
AD_UserAttributes = 'mail','sAMAccountName',

ad_fil = 'proxyAddresses',
ReOpenLDAP_ContactsFilter = "(&(objectClass=inetOrgPerson)(mail=*))"
ReOpenLDAP_ContactsAttributes= 'mail','uid'
ReOpenLDAP_ContactAttributes = 'displayName', 'mail', 'cn', 'sn', 'l', 'ou', 'title', 'telephoneNumber', 'objectclass','uid'
AD = ldap.initialize(AD_Server)
AD.sizelimit = 5000
AD.set_option(ldap.OPT_REFERRALS,0)

# Подключаемся а AD и получаем список групп пользователя
AD.simple_bind_s(AD_Bind_User, AD_Bind_Pass)
AD_User = AD.search_s(AD_BaseDN, ldap.SCOPE_SUBTREE, AD_UserFilter, ad_fil)

# Подключаемся к ReOpenLDAP
ReOpenLDAP = ldap.initialize(ReOpenLDAP_Server)
ReOpenLDAP.simple_bind_s(ReOpenLDAP_Bind_User, ReOpenLDAP_Bind_Pass)

#Список пользователей
user = AD_User
#Список в который будет состоять из номеров элементов списка user, в которых имеется proxyAddresses
prox_list = []
for i in range(len(user)):
    if 'proxyAddresses' in str(user[i]):
        prox_list+=[i]
    else:
        pass
print(len(prox_list)) # proxyaddresses

smtp = [] #index smtp
SMTP = [] #indes SMTP
mail_smtp = []
mail_SMTP = []
dic = {}

for i in prox_list:
    check = user[i][1]['proxyAddresses'] # список мэилов из proxylist
    for j in range(len(check)):
        lol = re.findall('smtp:\w+.(@\w+)',check[j])
        if len(lol) != 0 and lol[0] == '@mintrans':
            smtp+=[i]
            mail_smtp+=[check[j]]

for i in smtp:
    check2 = user[i][1]['proxyAddresses']
    for j in range(len(check2)):
              mem = re.findall('SMTP:\w',check2[j])
              if mem:
                  SMTP+=[i]
                  mail_SMTP+=[check2[j]]

for i in range(len(mail_smtp)-2):
    dic[mail_smtp[i]] = mail_SMTP[i]

print(len(smtp))#SMTP
print(len(SMTP))#smtp
print(dic)
