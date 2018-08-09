#!/usr/bin/python
#coding: utf-8

# Подключаем доп. модули
import ldap, re, os, time, getpass
import ldap.modlist as modlist

# определяем переменные
User = getpass.getuser()
AD_Server = 'ldap://...' # Server address
AD_BaseDN = 'DC=int,DC=domain,DC=ru'
AD_UserFilter = '(&(objectClass=user)(mail=*)(!(description=hide)))'
user_filter = 'memberOf','mail'  # for groups
AD_UserAttributes = 'displayName', 'mail', 'cn', 'sn', 'l', 'ou', 'title', 'telephoneNumber', 'sAMAccountName'
AD_Bind_User = 'CN=Manager,OU=Service,DC=int,DC=domain,DC=ru'
AD_Bind_Pass = '...' # Password
ReOpenLDAP_Server = 'ldap://...' # Server address
ReOpenLDAP_Bind_User = 'CN=Manager,DC=int,DC=domain,DC=ru'
ReOpenLDAP_Bind_Pass = '...' # Password
ReOpenLDAP_BaseDN = 'OU=CAB,DC=int,DC=domain,DC=ru'
ReOpenLDAP_ContactsFilter = "(&(objectClass=inetOrgPerson)(mail=*))"
ReOpenLDAP_ContactsAttributes= 'mail','uid'
ReOpenLDAP_ContactAttributes = 'displayName', 'mail', 'cn', 'sn', 'l', 'ou', 'title', 'telephoneNumber', 'objectclass','uid'
result =""
AD = ldap.initialize(AD_Server)
AD.sizelimit = 5000
AD.set_option(ldap.OPT_REFERRALS,0)


# Подключаемся а AD и получаем список групп пользователя
AD.simple_bind_s(AD_Bind_User, AD_Bind_Pass)
AD_g_mail = AD.search_s(AD_BaseDN, ldap.SCOPE_SUBTREE, 'objectClass=group',['mail','member','cn'])
AD_User = AD.search_s(AD_BaseDN, ldap.SCOPE_SUBTREE, 'objectClass=user',['cn','mail'])
AD_Users = AD.search_s(AD_BaseDN, ldap.SCOPE_SUBTREE, AD_UserFilter, AD_UserAttributes) # Для первой части скрипта

# Подключаемся к ReOpenLDAP
ReOpenLDAP = ldap.initialize(ReOpenLDAP_Server)+
ReOpenLDAP.simple_bind_s(ReOpenLDAP_Bind_User, ReOpenLDAP_Bind_Pass)



#####################Your part#########################

def One():
    for i in range(len(AD_User)-3): 
    #собираем набор аттрибутов пользователя AD
        attrs = {}
        attrs['objectClass'] = ['top','inetOrgPerson','organizationalPerson','person']
        if AD_User[i][1].get('cn') is not None: attrs['cn'] = AD_User[i][1]['cn'][0]
        if AD_User[i][1].get('displayName') is not None: attrs['displayName'] = AD_User[i][1]['displayName'][0]
        if AD_User[i][1].get('sn') is not None: attrs['sn'] = AD_User[i][1]['sn'][0]
        else: 
           space = attrs['displayName'].find(" ")
           if space == -1: attrs['sn'] = attrs['displayName']
           else: attrs['sn'] = attrs['displayName'][:space]
        if AD_User[i][1].get('mail') is not None: attrs['mail'] = AD_User[i][1]['mail'][0]
        if AD_User[i][1].get('l') is not None: attrs['l'] = AD_User[i][1]['l'][0]
        if AD_User[i][1].get('ou') is not None: attrs['ou'] = AD_User[i][1]['ou'][0]
        if AD_User[i][1].get('title') is not None: attrs['title'] = AD_User[i][1]['title'][0]
        if AD_User[i][1].get('telephoneNumber') is not None: attrs['telephoneNumber'] = AD_User[i][1]['telephoneNumber'][0]
        if AD_User[i][1].get('sAMAccountName') is not None: attrs['uid'] = AD_User[i][1]['sAMAccountName'][0]
    # ищем, есть ли такой-же контакт в ReOpenLdap
        ReOpenLDAP_ContactFilter = '(&(objectClass=inetOrgPerson)(mail=' + AD_User[i][1]['mail'][0] + '))'
        ReOpenLDAP_Contact = ReOpenLDAP.search_s(ReOpenLDAP_BaseDN, ldap.SCOPE_SUBTREE, ReOpenLDAP_ContactFilter, ReOpenLDAP_ContactAttributes)
        ReOpenLDAP_DN = 'mail=' + AD_User[i][1]['mail'][0] + "," + ReOpenLDAP_BaseDN
        if not ReOpenLDAP_Contact:
        # Если нет, создаем контакт в ReOpenLDAP 
            ldif = modlist.addModlist(attrs)
            ReOpenLDAP.add_s(ReOpenLDAP_DN,ldif)
        else:
        # если контакт есть, сравниваем аттрибуты. Если есть оличие - меняем аттрибуты контакта сгласно аттрибктам пользователя в AD
            attrs2 = ReOpenLDAP_Contact[0][1]
            attrs3 = {}
            for key in attrs2:
                attrs3[key] = attrs2[key][0]    
                attrs3['objectClass'] = ['top','inetOrgPerson','organizationalPerson','person']
            if cmp(attrs,attrs3) !=0:
                ldif = modlist.modifyModlist(attrs3,attrs)
                ReOpenLDAP.modify_s(ReOpenLDAP_DN,ldif)

    #Создаем списки пользователей AD и контактов ReOpenLdap (для простоты - только аттрибут почтовый ящик)
    AD_list=[]
    for i in range(len(AD_User)-3): AD_list.append(AD_User[i][1]['mail'][0])
    ReOpenLDAP_Contacts = ReOpenLDAP.search_s(ReOpenLDAP_BaseDN, ldap.SCOPE_SUBTREE, ReOpenLDAP_ContactsFilter, ReOpenLDAP_ContactsAttributes)
    ReOpenLDAP_list=[] 
    for i in range(len(ReOpenLDAP_Contacts)): ReOpenLDAP_list.append(ReOpenLDAP_Contacts[i][1]['mail'][0])
    # Вычленяем контакты для которых нет соответствующего пользователя. Их нужно удалять.
    old_contacts = set(ReOpenLDAP_list) - set(AD_list)
    for old_contact in old_contacts:
        # Удаляем лишние контакты из ReOpenLDAP
        ReOpenLDAP_DeleteDN = 'mail=' + old_contact + "," + ReOpenLDAP_BaseDN 
        ReOpenLDAP.delete_s(ReOpenLDAP_DeleteDN)
    AD.unbind_s()
    ReOpenLDAP.unbind_s()


####################My part#########################

def Two(): 
    mas = []
    mailGroup = []
    count = -1
    for i in range(len(AD_g_mail)):
        if 'mail' in str(AD_g_mail[i]) and 'member' in str(AD_g_mail[i]):
            mas.append(i)                              # id group list
            mailGroup+=AD_g_mail[i][1]['mail']        # email group list

# print(mas) 
    print(mailGroup)

    result = []

    for i in mas:
        b = []
        a = []
        umail = []
        count+=1;
        group = AD_g_mail[i][1]['member']
        cn = AD_g_mail[i][1]['cn']
        mail = mailGroup[count]
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

    for i in range(len(result)):         #Группы
        groupADCn = result[i][0][0]
        mailOfUsers = result[i][1]
        groupADMail = result[i][0][1]
        #check AD group in LDAP
        ReOpenLDAPGroup = '(&(objectClass=extensibleObject)(mail=' +groupADMail+ '))'
        ReOpenLDAPFindGroup = ReOpenLDAP.search_s(ReOpenLDAP_BaseDN, ldap.SCOPE_SUBTREE, ReOpenLDAPGroup, ReOpenLDAP_ContactAttributes)
        if not ReOpenLDAPFindGroup: 
            # Create 
            groupAttr = {}
            groupAttr['ObjectClass'] = ['top','person','extensibleObject']
            groupAttr['cn'] = groupADCn
            groupAttr['sn'] = groupADCn
            pseudo = [] # list for pseudonims
            for j in mailOfUsers:
                pseudo += [j] # mailof ad users = ldap pseudonims list
            groupAttr['pseudonym'] = pseudo
            print(groupAttr)
            forCreate = 'mail=' + groupADMail + "," + ReOpenLDAP_BaseDN
            mdlistGroup = modlist.addModlist(groupAttr)
            print(forCreate)
            print(mdlistGroup)
        #ReOpenLDAP.add_s(forCreate,mdlistGroup)
        else:
            pass
if __name__=="__main__":
    One()
    Two()