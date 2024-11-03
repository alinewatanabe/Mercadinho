from PyQt5.QtCore import QThread, pyqtSignal
import serial


class RFIDReaderThread(QThread):
    rfid_read = pyqtSignal(str)  # Sinal emitido quando um RFID é lido

    def __init__(self, parent=None):
        super().__init__(parent)
        self.reading_rfid = True  # Controle para parar a leitura
        self.ser = serial.Serial(port="COM5", baudrate=9600)

    def run(self):
        """Função executada em uma thread separada."""
        while self.reading_rfid:
            try:
                value = self.ser.readline()
                rfid_code = str(value, "utf-8").strip()  # Remove espaços em branco
                self.rfid_read.emit(rfid_code)  # Emite o sinal com o RFID lido
            except serial.SerialException as e:
                print(f"Erro na leitura da porta serial: {e}")
                break

    def stop(self):
        """Para a leitura do RFID."""
        self.reading_rfid = False
        self.ser.close()
