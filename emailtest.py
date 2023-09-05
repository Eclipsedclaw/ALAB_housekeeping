import smtplib as smt
from email.message import EmailMessage
import serial
import time


server = "smtp.gmail.com"
port = 587
gmail_username = "gramsuser@gmail.com"
gmail_pass = "rydqzoykdkdelgke" # replace with password when testing

timesince = 0
togglelow = 0

class Mailer:
    def sendmail(self, toppress, flag):
        to = ["suraj.a@northeastern.edu"]

        session = smt.SMTP(server, port)
        session.ehlo()
        session.starttls()
        session.ehlo()

        message_high = "TEST MESSAGE BELOW\nALERT: The pressure in the main chamber is %02f torr." % toppress
        message_low = "TEST MESSAGE BELOW\nNOTICE: The pressure is now %02f torr, which is below the threshold of 1500 torr." % toppress
        msg = EmailMessage()

        session.login(gmail_username, gmail_pass)

        msg["From"] = "gramsuser@gmail.com"
        msg["To"] = to[0]
        if flag == "H":
            msg["Subject"] = "Pressure high alert"
            msg.set_content(message_high)
            session.sendmail(gmail_username, to, msg.as_string())
        elif flag == "L":
            msg["Subject"] = "Normal pressure level restored"
            msg.set_content(message_low)
            session.sendmail(gmail_username, to, msg.as_string())

        session.quit()


Gauge1 = serial.Serial()
toppath = "/dev/toppress"
Gauge1.baudrate = 9600
Gauge1.parity = 'N'
Gauge1.stopbits = 1
Gauge1.bytesize = 8

topstat = 1
flg = True
T_sleep = 0.6

def loop():
    while True:
        global Gauge1, topstate, timesince, togglelow
        if topstat == 1:
            flag3 = 0
            Gauge1 = serial.Serial(toppath)
            Gauge1.write(('$@001PR3?;FF').encode('utf8'))
            time.sleep(2*T_sleep)
            GaugeP1 = Gauge1.read(Gauge1.inWaiting()).decode('utf8')
            while (len(GaugeP1) != 17 and flag3 <= 3):
                try:
                    print ('Pressure gauge (P1) readout error')
                    Gauge1.write(('$@001PR3?;FF').encode('utf8'))
                    time.sleep(T_sleep)
                    GaugeP1 = Gauge1.read(Gauge1.inWaiting()).decode('utf8')
                    print(GaugeP1 + " ;len = " +str(len(GaugeP1)))
                    flag3 += 1
                except UnicodeDecodeError:
                    print ("Decode error, skipping this entry.")
                    pass
                #@253ACK6.41E+2;FF
            if len(GaugeP1) == 17:
                P1_tmp = float(GaugeP1[7:14])
                print (P1_tmp)
                timenow = time.perf_counter()
                if (P1_tmp > 650.0 and timenow - timesince > 3600.0):
                    alert = Mailer()
                    alert.sendmail(P1_tmp, "H")
                    timesince = time.perf_counter()
                    togglelow = 1
                elif (P1_tmp < 650.0 and togglelow == 1):
                    notice = Mailer()
                    notice.sendmail(P1_tmp, "L")
                    togglelow = 0
        elif topstat == 0:
            print("Top pressure gauge port not found/open")
            P1_tmp = None

loop()
