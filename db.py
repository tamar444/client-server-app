import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  database="uplata_humanitarne_pomoci"
)


def sacuvaj_uplatu(ime_prezime,datum,vreme,iznos):
    with mydb.cursor() as cursor:
        tuple1 = (ime_prezime,datum,vreme,iznos)
        cursor.execute('INSERT INTO payments (ime_prezime,datum,vreme,iznos) VALUES (%s, %s, %s, %s)', tuple1)
        mydb.commit()

def da_li_postoji_u_bazi(brk,cvv):
  with mydb.cursor() as cursor:
    cursor.execute("SELECT * FROM cards WHERE broj_kartice = %s AND vcc = %s", (brk, cvv))
    result=cursor.fetchone()
  return result is not None

def brk_za_cvv(username):
  with mydb.cursor() as cursor:
    cursor.execute("SELECT broj_kartice FROM users WHERE username = %s", (username,))
    result=cursor.fetchone()
  return result[0]
   

def vrati_poslednjih_10_uplata():
    formatirano=''
    with mydb.cursor() as cursor:
        cursor.execute("SELECT * FROM payments ORDER BY id DESC LIMIT 10")
        result = cursor.fetchall()
        if not result:
            return "Nema dostupnih uplata."
        for item in result:
         formatirano+=f'Ime i prezime: {item[1]}, Datum: {item[2]}, Vreme: {item[3]}, Iznos: {item[4]}\n'
    return formatirano

def vrati_ukupno():
   with mydb.cursor() as cursor:
      cursor.execute('SELECT SUM(iznos) FROM payments')
      return cursor.fetchone()[0]
   
def registracija(username,password,ime,prezime,jmbg,broj_kartice,email):
   tuple1=(username,password,ime,prezime,jmbg,broj_kartice,email)
   with mydb.cursor() as cursor:
      cursor.execute('SELECT * FROM users WHERE username=%s',(username,))
      if not cursor.fetchone():
        cursor.execute(
           'INSERT INTO users (username,password,ime,prezime,jmbg,broj_kartice,email) VALUES (%s, %s, %s, %s,%s,%s,%s)',tuple1)
        mydb.commit()
        return True
      else:
        return False

def login(username,password):
   with mydb.cursor() as cursor:
      cursor.execute('SELECT * FROM users WHERE username=%s and password=%s',(username,password))
      result=cursor.fetchone()
   return result is not None