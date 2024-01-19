from socket import *
from threading import *
from re import *
from db import *
from datetime import datetime

                 
class ClientHandler(Thread):
    def __init__(self, client_sock, client_address):
        self.sock = client_sock
        self.address = client_address
        self.prijavljen=False
        self.izlaz=False
        self.username='x'
        super().__init__()
        self.start()

    def run(self):
       
     while not self.izlaz:

        def is_brk_valid(brk):
            pattern = compile(r'^\d{4}-\d{4}-\d{4}-\d{4}$')
            return bool(pattern.match(brk))
        
        def is_exit(poruka):
            if poruka.lower() == 'exit':
                return True
            return False

        def uplata_pomoci():
                try:
                    self.sock.send('Unesite svoje ime i prezime (npr. Petar Petrovic):\n>>'.encode())
                    imep = self.sock.recv(4096).decode()
                    if is_exit(imep): return
                    self.sock.send('Unesite svoju adresu:\n>>'.encode())
                    adresa = self.sock.recv(4096).decode()
                    if is_exit(adresa): return
                            
                    while True:
                        self.sock.send('Unesite CVV broj (mora biti trocifren):\n>>'.encode())
                        cvv = self.sock.recv(4096).decode()
                        if is_exit(cvv): return
                        is_cvv_valid=cvv.isdigit() and len(cvv)==3
                        if self.prijavljen and is_cvv_valid and da_li_postoji_u_bazi(brk_za_cvv(self.username),cvv):
                            break
                        if is_cvv_valid and not self.prijavljen:
                            break
                        self.sock.send('CVV broj nije ispravan, pokusajte ponovo.'.encode())

                    while True:
                        if self.prijavljen:
                          break
                        self.sock.send('Unesite broj svoje platne kartice u formatu xxxx-xxxx-xxxx-xxxx:\n>>'.encode())
                        brk = self.sock.recv(4096).decode()
                        if is_exit(brk): return
                        if is_brk_valid(brk) and da_li_postoji_u_bazi(brk,cvv):
                            break
                        self.sock.send('Broj kartice nije u ispravnom formatu ili ne postoji u bazi, pokusajte ponovo.'.encode())


                    while True:
                        self.sock.send('Unesite iznos koji zelite uplatiti (minimum 200 dinara):\n>>'.encode())
                        iznos_uplate = self.sock.recv(4096).decode()
                        if is_exit(iznos_uplate): return
                        is_uplata_valid = iznos_uplate.isdigit() and int(iznos_uplate)>=200
                        if is_uplata_valid:
                            break
                        self.sock.send('Uplata mora biti veca od 200 dinara, pokusajte ponovo.'.encode())

                    datum=datetime.now().strftime("%d-%m-%Y")
                    vreme=datetime.now().strftime("%H:%M:%S")
                    podaci_korisnika='Potvrda:\n'+imep+'  '+'   '+adresa+'   '+datum+'    '+vreme+'   '+iznos_uplate
                    self.sock.send(podaci_korisnika.encode())
                    self.sock.send('Uspesna uplata! Potvrda o ovoj uplati je poslata.'.encode())

                    sacuvaj_uplatu(imep,datum,vreme,iznos_uplate)
                except:
                    print('Klijent je prekinuo komunikaciju.')


        def pregled_sredstava():
            novac=vrati_ukupno()
            poruka=f'Kolicina ukupno sakupljenih sredstava: {novac} din.'
            self.sock.send(poruka.encode())

        def registracija_korisnika():
            try:
                while True:
                    self.sock.send('Unesite svoje ime:\n>>'.encode())
                    ime=self.sock.recv(4096).decode()
                    if is_exit(ime): return
                    is_ime_valid=len(ime.strip()) != 0
                    if is_ime_valid:   
                        break
                    self.sock.send('Ovo polje ne sme biti prazno! Pokusajte ponovo.'.encode()) 
                while True:
                    self.sock.send('Unesite svoje prezime:\n>>'.encode())
                    prezime=self.sock.recv(4096).decode()
                    if is_exit(prezime): return
                    is_prezime_valid=len(prezime.strip()) != 0
                    if is_prezime_valid:
                        break
                    self.sock.send('Ovo polje ne sme biti prazno! Pokusajte ponovo.'.encode())
                while True:
                    self.sock.send('Unesite svoj JMBG:\n>>'.encode())
                    jmbg=self.sock.recv(4096).decode()
                    if is_exit(jmbg): return
                    is_jmbg_valid=jmbg.isdigit and len(jmbg.strip()) == 13
                    if is_jmbg_valid:  
                        break
                    self.sock.send('Ovo polje mora sadrzati 13 cifara! Pokusajte ponovo.'.encode())
                while True:
                    self.sock.send('Unesite broj platne kartice:\n>>'.encode())
                    brk = self.sock.recv(4096).decode()
                    if is_exit(brk): return
                    if is_brk_valid(brk):
                        break
                    self.sock.send('Broj kartice nije u ispravnom formatu! Pokusajte ponovo.'.encode())
                while True:
                    self.sock.send('Unesite svoj mail:\n>>'.encode())
                    mail=self.sock.recv(4096).decode()
                    if is_exit(mail): return
                    if '@' in mail:
                        break
                    self.sock.send('Unesena mail adresa nije validna, neophodno je da sadrzai znak \'@\'. Pokusajte ponovo.'.encode())
                while True:
                    self.sock.send('Unesite lozinku (minimum 7 karaktera):\n>>'.encode())
                    password=self.sock.recv(4096).decode()
                    if is_exit(password): return
                    is_password_valid=len(password)>=7
                    if is_password_valid:
                        break
                    self.sock.send('Lozinka mora sadrzati minimum 7 karaktera. Pokusajte ponovo.'.encode())
                while True:
                    self.sock.send('Unesite korisnicko ime:\n>>'.encode())
                    username=self.sock.recv(4096).decode()
                    if is_exit(username): return
                    if registracija(username,password,ime,prezime,jmbg,brk,mail):
                        self.sock.send('Uspesno ste se registrovali!'.encode())
                        break
                    self.sock.send('Ovo korisnicko ime je vec zauzeto. Pokusajte ponovo.'.encode())
            except:
                    print('Klijent je prekinuo komunikaciju.')  

        def prijava_korisnika():
            try:
                while True:
                    self.sock.send('Unesite korisnicko ime:\n>>'.encode())
                    username=self.sock.recv(4096).decode()
                    if is_exit(username): return
                    self.sock.send('Unesite lozinku:\n>>'.encode())
                    password=self.sock.recv(4096).decode()
                    if is_exit(password): return
                    if login(username,password):
                            self.prijavljen = True
                            self.username=username
                            self.sock.send('Uspesno ste se ulogovali!'.encode())
                            break
                    self.sock.send('Uneti kredencijali nisu ispravni! Pokusajte ponovo.'.encode())
            except:
                print('Klijent je prekinuo komunikaciju.')

        def pregled_transakcija():
            if not self.prijavljen:
                self.sock.send('Potrebno je da se prijavite kako biste mogli da pregledate nedavne transakcije!'.encode())
                return
            uplate=vrati_poslednjih_10_uplata()
            self.sock.send(uplate.encode())

        def meni():
            try:
                self.sock.send(opcije.encode())
                odabir = self.sock.recv(4096).decode()
                if odabir== '1':
                    registracija_korisnika()
                elif odabir== '2': 
                    prijava_korisnika()
                elif odabir== '3':
                    uplata_pomoci()
                elif odabir== '4':
                    pregled_sredstava()
                elif odabir=='5':
                    pregled_transakcija()
                elif odabir=='6':
                    self.sock.send('Dovidjenja!'.encode())
                    self.sock.close()
                    self.izlaz=True
                else:
                    self.sock.send('Pogresan odabir! Pokusajte ponovo.'.encode())
                    meni()
            except:
                    print('Klijent je prekinuo komunikaciju.')

                    self.izlaz=True
        meni()





opcije = '''Odaberite broj koji se nalazi ispred željene opcije:
1.Registracija
2.Prijava
3.Uplata pomoći
4.Pregled ukupno sakupljenih sredstava
5.Pregled transakcija
6.Izlaz
Ukoliko se u bilo kom trenutku zelite vratiti na meni, ukucajte 'exit'.\n>> '''

server_adress = 'localhost'
server_port = 2222
server_sock = socket(AF_INET, SOCK_STREAM)
server_sock.bind((server_adress, server_port))

server_sock.listen()

if __name__ == '__main__':
    print('Listening...')
    while True:
        client_sock, client_adress = server_sock.accept()
        client=ClientHandler(client_sock,client_adress)
