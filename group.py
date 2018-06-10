#!/usr/bin/python
#coding: utf-8

# Подключаем доп. модули
import ldap, re, os, time, getpass
import ldap.modlist as modlist

# определяем переменные
User = getpass.getuser()
AD_Server = 'ldap://'
AD_BaseDN = 'DC=,DC=,DC='
user_filter = 'memberOf','mail'

AD_Bind_User = ''
AD_Bind_Pass = ''
AD = ldap.initialize(AD_Server)
AD.sizelimit = 5000
AD.set_option(ldap.OPT_REFERRALS,0)


# Подключаемся а AD и получаем список групп пользователя
AD.simple_bind_s(AD_Bind_User, AD_Bind_Pass)
AD_g_mail = AD.search_s(AD_BaseDN, ldap.SCOPE_SUBTREE, 'objectClass=group',['mail','member','cn'])
AD_User = AD.search_s(AD_BaseDN, ldap.SCOPE_SUBTREE, 'objectClass=user',['cn','mail'])

mas = []
mail_group = []
count = -1

for i in range(len(AD_g_mail)):
    if 'mail' in str(AD_g_mail[i]) and 'member' in str(AD_g_mail[i]):
        mas.append(i)                              # id group list
        mail_group+=AD_g_mail[i][1]['mail']        # email group list

print(mas)
print(mail_group)

result = []

for i in mas:
      b = []
      a = []
      umail = []
      count+=1;
      group = AD_g_mail[i][1]['member']
      cn = AD_g_mail[i][1]['cn']
      mail = mail_group[count]
      a+=cn
      a+=[mail]
      for j in range(len(group)):
          users = AD.search_s(group[j], ldap.SCOPE_SUBTREE, 'objectClass=user',['cn','mail'])
          if len(users) == 1:
              if 'mail' in str(users):
                  umail+=[users[0][1]['mail'][0]]
          contacts = AD.search_s(group[j], ldap.SCOPE_SUBTREE, 'objectClass=contact',['cn','mail'])
          if len(contacts) == 1:
              if 'mail' in str(contacts):
                  umail+=[contacts[0][1]['mail'][0]]
      b.append(a)
      b.append(umail)
      result.append(b)
print(result)
