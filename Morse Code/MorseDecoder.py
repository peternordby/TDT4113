import time
from GPIOSimulator_v1 import *
GPIO = GPIOSimulator()

MORSE_CODE = {'.-': 'a', '-...': 'b', '-.-.': 'c', '-..': 'd', '.': 'e', '..-.': 'f', '--.': 'g',
              '....': 'h', '..': 'i', '.---': 'j', '-.-': 'k', '.-..': 'l', '--': 'm', '-.': 'n',
              '---': 'o', '.--.': 'p', '--.-': 'q', '.-.': 'r', '...': 's', '-': 't', '..-': 'u',
              '...-': 'v', '.--': 'w', '-..-': 'x', '-.--': 'y', '--..': 'z', '.----': '1',
              '..---': '2', '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
              '---..': '8', '----.': '9', '-----': '0'}

class MorseDecoder():
    current_symbol = ""
    current_word = ""
    current_sentence = []
    morse_sentence = []

    def __init__(self):
        """
        Sets up IO ports for GPIO Simulator
        """

        GPIO.setup(PIN_BTN, GPIO.IN, GPIO.PUD_UP)
        GPIO.setup(PIN_RED_LED_0, GPIO.OUT, GPIO.LOW)
        GPIO.setup(PIN_BLUE_LED, GPIO.OUT, GPIO.LOW)

    def read_signals(self):
        """
        Reads signal coming from button input and makes sure it is valid
        Raises KeyboardInterrupt error when pressing Ctrl+C to escape infinite loop
        """

        last_state_BTN = 0                                
        stop = 0
        try:
            while True:
                time.sleep(0.01)
                input = GPIO.input(PIN_BTN)
                input_check = GPIO.input(PIN_BTN)                   #Compare two button inputs to lower chance of false press
                
                #Goes from low to high (Button is pressed)
                if last_state_BTN == 0 and input == input_check == 1:
                    pause = time.time() - stop
                    last_state_BTN = 1
                    start = time.time()
                    if stop != 0:
                        if 0.4 < pause < 2:                         #Medium pause signal 0.4 - 2 seconds
                            print(" ", end="", flush=True)
                            self.process_signal(2)
                        elif pause > 2:                             #Long pause signal > 2 seconds
                            print("\n", end="", flush=True)
                            self.process_signal(3)

                #Goes from high to low (Button is released)
                if last_state_BTN == 1 and input == input_check == 0:
                    duration = time.time() - start
                    last_state_BTN = 0
                    stop = time.time()
                    if duration < 0.3:                              #Dot < 0.3 seconds
                        print(".", end="", flush=True)           
                        self.process_signal(0)
                        #GPIO.output(PIN_RED_LED_0, GPIO.HIGH)   
                        #GPIO.output(PIN_RED_LED_0, GPIO.LOW)
                    elif duration > 0.3:                            #Dash > 0.3 seconds
                        print("-", end="", flush=True)                   
                        self.process_signal(1)
                        #GPIO.output(PIN_BLUE_LED, GPIO.HIGH)    
                        #GPIO.output(PIN_BLUE_LED, GPIO.LOW)

        #Terminates program when pressing Ctrl+C
        except KeyboardInterrupt:
            self.process_signal(3)
            self.show_final_message()
                                                                       
    def process_signal(self, signal):
        if signal == 0:
            self.update_current_symbol(".")
        elif signal == 1:
            self.update_current_symbol("-")
        elif signal == 2:
            self.handle_symbol_end()
        elif signal == 3:
            self.handle_word_end()

    def update_current_symbol(self, signal):
        self.current_symbol += signal

    def handle_symbol_end(self):
        if self.current_symbol in MORSE_CODE:
            letter = MORSE_CODE[self.current_symbol]
            self.current_sentence.append(letter)
            self.morse_sentence.append(self.current_symbol + " ")
        self.current_symbol = ""

    def handle_word_end(self):
        self.handle_symbol_end()
        self.current_sentence.append(" ")
        self.morse_sentence.append(" ")

    def show_final_message(self):
        print("\n\nThe final message is: " + "".join(self.current_sentence).strip() + "\n" + "".join(self.morse_sentence).strip() + "\n")

def main():
    decode = MorseDecoder()
    decode.read_signals()                             

if __name__ == "__main__":
    main()






    