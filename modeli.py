import sqlite3
import datetime
import dobi_zneske
con = sqlite3.connect('Kriptovalute.db')
cur = con.cursor()

###########################################################################
#                                                                         #
#                           OSEBNI PODATKI LASTNIKA                       #
#                                                                         #
###########################################################################

def mail_v_bazi(mail):
    sql = '''SELECT 1 FROM oseba WHERE mail = ?'''
    cur = con.execute(sql, [mail])
    return cur.fetchall()

def mail(username):
    cur = con.execute("SELECT mail FROM oseba WHERE mail=(?)",
                  [username])
    return cur.fetchone()


def podatki_vsi():
    '''funckija vrne vse lastnike'''
    sql = '''SELECT * FROM oseba'''
    cur = con.execute(sql)
    return cur.fetchall()

def podatki(id_st):
    '''funckija vrne ime lastnika z id_st-jem id'''
    sql = '''SELECT *
            FROM oseba
            WHERE id = ?'''
    for pod in con.execute(sql,[id_st]):
        return pod

def ime(id_st):
    '''funckija vrne ime lastnika z id_st-jem id'''
    sql = '''SELECT ime
            FROM oseba
            WHERE id = ?'''
    for ime in con.execute(sql,[id_st]):
        return ime[0]

def priimek(id_st):
    '''funckija vrne priimek lastnika z id-jem id'''
    sql = '''SELECT priimek
            FROM oseba
            WHERE id = ?'''
    for priimek in con.execute(sql,[id_st]):
        return priimek[0]

def geslo(id_st):
    '''funckija vrne md5 geslo lastnika z id_st-jem id'''
    sql = '''SELECT geslo
            FROM oseba
            WHERE id = ?'''
    for geslo in con.execute(sql,[id_st]):
        return geslo[0]

def id_st(mail):
    '''funckija vrne id lastnika z mailom
    za prijavo preko maila.'''
    sql = '''SELECT id
            FROM oseba
            WHERE mail = ?'''
    for id_s in con.execute(sql,[mail]):
        return id_s[0]

def id_je_v_bazi(id):
    '''Funkcija vrne True ali False glede na to, če id je v bazi'''
    sql = '''SELECT id FROM oseba'''
    sezID = []
    for idVBazi in con.execute(sql):
        sezID.append(idVBazi[0])
    # pogledamo če id je v bazi
    return id in set(sezID)


def poisci_osebo(ime, priimek):
    ''' funkcija poisce lastnike, ki imajo skupne podatke ime, priimek'''
    sql =''' SELECT id, ime, priimek, mail, stanje FROM oseba WHERE ime LIKE ? AND priimek LIKE ? '''
    sezOseb = []
    for id, ime, priimek, mail, geslo in con.execute(sql, ['%'+ime+'%', '%'+priimek+'%']):
        sezOseb.append([id, ime, priimek, mail, geslo])
    return sezOseb


def seznam_valut():
    sql = '''SELECT * FROM Valuta'''
    sez = []
    podatki = dobi_zneske.vrni_podatke()
    for k, ime in con.execute(sql):
        spletna = dobi_zneske.generiraj_spletno(ime.lower())
        vrednost, evri, cas = podatki.get(ime.lower(),(0,0,0))
        if (vrednost, cas) != (0, 0):
            sez.append((k, ime, spletna, vrednost, evri, dobi_zneske.datum(cas)))
    return sez

def ime_valute(id):
    sql = '''SELECT ime FROM Valuta
    WHERE id = (?)'''
    for ime in con.execute(sql,[id]):
        return ime[0]

def kupljene_valute(id):
    sql = '''SELECT valuta, vrednost,
    SUM(kolicina) as kolicina, max(Datum) as datum FROM lastnistvo_valut
    WHERE (SELECT id FROM Oseba
    WHERE lastnistvo_valut.lastnik = (?))
    GROUP BY valuta'''
    sez = []
    for valuta, vrednost, kolicina, datum in con.execute(sql,[id]):
        sez.append((valuta, ime_valute(valuta), vrednost, kolicina, datum))
    return sez


def zasluzek(id):
    sql='''SELECT Valuta,-SUM(kolicina* cena)
    FROM Zgodovina WHERE (?) = Oseba
    GROUP BY Oseba, Valuta'''
    sez = [[],[]]
    for valuta,vrednost in con.execute(sql,[id]):
        if vrednost >= 0:
            sez[0].append([valuta,round(vrednost,2)])
        else:
            sez[1].append([valuta,round(vrednost,2)])
    return sez

def vrni_zgodovino(id):
    '''[id, valuta, kolicina, cena, datum]'''
    sez = []
    sql='''SELECT * FROM Zgodovina WHERE
Zgodovina.Oseba = (?)'''
    for el in con.execute(sql, [id]):
        sez.append(el)
    return sez

def izpis_lastnikov_valut():
    sql = '''SELECT Oseba.ime, Oseba.priimek,Oseba.mail,valuta.ime,
    lastnistvo_valut.kolicina, lastnistvo_valut.vrednost,lastnistvo_valut.Datum FROM Oseba 
    JOIN lastnistvo_valut ON Oseba.id = lastnistvo_valut.lastnik
    JOIN Valuta on Valuta.id = lastnistvo_valut.valuta'''
    return list(con.execute(sql))

def izpis_lastnikov_valute(valuta):
    sql = '''SELECT Oseba.ime, Oseba.priimek,Oseba.mail,valuta.ime,
    lastnistvo_valut.kolicina, lastnistvo_valut.vrednost,lastnistvo_valut.Datum FROM Oseba 
    JOIN lastnistvo_valut ON Oseba.id = lastnistvo_valut.lastnik
    JOIN Valuta on Valuta.id = lastnistvo_valut.valuta
    WHERE Valuta.id = (?)'''
    return list(con.execute(sql,[valuta]))

def lozerji():
    sql = '''SELECT id, ime, priimek, mail, -SUM(kolicina*cena) FROM Oseba
    JOIN Zgodovina ON Oseba.id = Zgodovina.Oseba
    GROUP BY mail
    HAVING -SUM(kolicina*cena) < 0'''
    return list(con.execute(sql))

def vrednost_valut():
    '''vrne koliko imajo osebe vredne valute'''
    sql = '''
    SELECT id, ime, priimek, mail, SUM(kolicina*vrednost) FROM lastnistvo_valut
JOIN Oseba ON lastnistvo_valut.lastnik = Oseba.id
GROUP BY mail'''
    return list(con.execute(sql))

###########################################################################
#                                                                         #
#                           DODAJANJE V BAZO                              #
#                                                                         #
###########################################################################

def dodaj_osebo(ime, priimek, mail, geslo):
    '''funkcija doda novega lastnika in sicer osnovne podatke'''
    sql = ''' INSERT INTO oseba (ime, priimek, mail, geslo)
              VALUES (?,?,?,?)'''
    con.execute(sql, [ime, priimek, mail, geslo])
    con.commit()

def dodaj_v_zgodovino(lastnik, valuta, kolicina, cena, datum = datetime.datetime.now()):
    sql = '''INSERT INTO Zgodovina (Oseba, Valuta, kolicina, cena)
            VALUES (?,?,?,?)'''
    con.execute(sql,[lastnik, valuta, kolicina, cena])
    con.commit()

def kupi_valuto(lastnik, valuta, vrednost, kolicina, datum = datetime.datetime.now()):
    sql = '''INSERT INTO lastnistvo_valut (lastnik, valuta, vrednost, kolicina)
              VALUES (?,?,?,?)'''
    dodaj_v_zgodovino(int(lastnik), valuta, float(kolicina), float(vrednost),datum)
    con.execute(sql,[int(lastnik), valuta, float(vrednost), float(kolicina)])
    con.commit()


def _dodaj_valute(naslov = 'https://bittrex.com/api/v1.1/public/getcurrencies'):
    ''' funkcija doda kriptovaluto v bazo'''
    sql = '''INSERT INTO Valuta (id, ime)
              VALUES (?,?)'''
    napaka = None
    try:
        for kratica, ime, _ in dobi_zneske.imena_valut(naslov):
            con.execute(sql,[kratica, ime])
    except Exception as e:
        napaka = e
    finally:
        con.commit()
    return napaka

def dodaj_valute():
    sql = '''DELETE FROM Valuta'''
    if _dodaj_valute():
        con.execute(sql)
        con.commit()
    _dodaj_valute()
    return

def dodaj_nove_valute(naslov = 'https://bittrex.com/api/v1.1/public/getcurrencies'):
    '''funkcija doda nove valute'''
    sql = '''SELECT ime FROM valuta'''
    sql_vstavi = '''INSERT INTO Valuta (id, ime)
              VALUES (?,?)'''
    mn = set()
    for valuta, in con.execute(sql):
        mn.add(valuta)
    for kratica, ime, _ in dobi_zneske.imena_valut(naslov):
        if ime not in mn:
            con.execute(sql_vstavi,[kratica, ime])
    con.commit()
    return
        
    


###########################################################################
#                                                                         #
#                           ODSTRANJEVANJE IZ BAZE                        #
#                                                                         #
###########################################################################

def prodaj_valuto(lastnik, valuta, kolicina,cena,vse=False):
    sql_1 = '''SELECT kolicina FROM lastnistvo_valut
    WHERE (SELECT id FROM oseba WHERE (SELECT id FROM Valuta
          WHERE (?) = lastnistvo_valut.lastnik AND (?) = lastnistvo_valut.valuta))'''
    for kol in con.execute(sql_1,[lastnik, valuta]):
        dodaj_v_zgodovino(lastnik,valuta,-float(kolicina),cena)
        prodaj = max(kol[0]-float(kolicina),0)
        if vse or prodaj==0:
            sql = '''DELETE FROM lastnistvo_valut 
                  WHERE (SELECT id FROM oseba WHERE (SELECT id FROM Valuta
                  WHERE (?) = lastnistvo_valut.lastnik AND (?) = lastnistvo_valut.valuta))'''
            con.execute(sql,[int(lastnik), valuta])
        else:
            sql = '''UPDATE lastnistvo_valut
              SET kolicina = (?), Datum = datetime('now')
              WHERE (SELECT id FROM oseba WHERE (SELECT id FROM Valuta
              WHERE (?) = lastnistvo_valut.lastnik AND (?) = lastnistvo_valut.valuta))'''
            con.execute(sql,[prodaj, int(lastnik), valuta])  
        con.commit()


def zbrisi_zgodovino(lastnik):
    sql = '''DELETE FROM Zgodovina
              WHERE (?) = Oseba'''
    con.execute(sql,[lastnik])
    con.commit()

def zbrisi_zgodovino_valuta(id):
    sql = '''DELETE FROM Zgodovina
              WHERE (?) = Valuta'''
    con.execute(sql,[id])
    con.commit()

def _zbrisi_valuto(id):
    sql = '''DELETE FROM Valuta
    WHERE id = (?)'''
    con.execute(sql,[id])
    con.commit()

def _zbrisi_valute(id):
    sql = '''DELETE FROM Valuta'''
    con.execute(sql)
    con.commit()

def zbrisi_valuto(id):
    for _, _, mail, _, kolicina, cena, _ in izpis_lastnikov_valute(id):
        id_s = id_st(mail)
        prodaj_valuto(id_s,id,kolicina,cena,True)
        zbrisi_zgodovino_valuta(id)
    _zbrisi_valuto(id)

def zbrisi_valute():
    for valuta,_,_,_,_,_ in seznam_valut():
        zbrisi_valuto(valuta)

def zbrisi_vse_osebe():
    for id,_,_,_,_ in podatki_vsi():
        zapri_racun(id)


def _zbrisi_osebo(id_osebe):
    ''' funkcija odstrani osebo'''
    sql = '''DELETE FROM oseba
    WHERE oseba.id = (?)'''
    con.execute(sql,[id_osebe])
    con.commit()

def zapri_racun(id_osebe):
    '''proda vse kriptovalute in zbriše osebo'''
    sql = '''SELECT * FROM lastnistvo_valut
    WHERE lastnik = (?)'''
    for id_o, id_valute, vrednost, kolicina, _ in con.execute(sql,[id_osebe]):
        prodaj_valuto(int(id_osebe), id_valute, kolicina,0.0,True)
        zbrisi_zgodovino(int(id_osebe))
    _zbrisi_osebo(id_osebe)


###########################################################################
#                                                                         #
#                           POSODABLJANJE BAZE                            #
#                                                                         #
###########################################################################

def spremeni_osebo(id, ime, priimek, mail, geslo):
    sql = ''' UPDATE oseba
                SET ime = (?), priimek = (?), mail = (?), geslo = (?)
              WHERE id = (?)'''
    con.execute(sql, [ime, priimek, mail, geslo, id])
    con.commit()    

###########################################################################
#                                                                         #
#                           POMOŽNE FUNKCIJE                              #
#                                                                         #
###########################################################################

def vsi_podatki(id_st):
    sez = []
    valute = seznam_valut()
    lastnistvo = kupljene_valute(id_st)
    for el in valute:
        kratica,ime,stran,vrednost_t,evri,datum=el
        for el in lastnistvo:
            kra,ime1,vrednost,kolicina,datum1=el
            if kratica == kra:
                sez.append((kra, ime, vrednost, vrednost_t, kolicina, datum1))
    return sez
                
