"""
ChatGPT splitter - Simple python script that cuts large pieces of text into segments inorder to easily have chatGPT digest large pieces of text.
Version 0.01

"""

import sys
import math
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel

# ChatGPTSplitter class is for the entire GUI
class ChatGPTSplitter(QMainWindow):
    start_chunk = 0
    end_chunk = 0
    current_chunk = 0
    chunks = []
    number_allowed_characters = 20000
    search_offset = 500

    # __init__(self)
    # self - GUI
    # Initialize GUI
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT Splitter")
        self.setGeometry(100, 100, 800, 1200)  # Adjust the size as needed

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.init_ui()

    # init_ui(self)
    # self - GUI
    # Initilize the GUI's components (buttons, text boxes, etc)
    def init_ui(self):
        vbox = QVBoxLayout()

        # Initilize the input section
        input_label = QLabel("Input:")
        self.input_textbox = QTextEdit()
        vbox.addWidget(input_label)
        vbox.addWidget(self.input_textbox)

        # Output Section with Backward, Forward buttons, Copy button, and chunk info
        output_label = QLabel("Output:")
        self.output_textbox = QTextEdit()
        # Chunk label to help visulize the chunks
        self.chunk_label = QLabel("0/0")
        hbox = QHBoxLayout()
        hbox.addWidget(output_label)
        hbox.addWidget(QPushButton("Backward", clicked=self.backward_chunk))
        hbox.addWidget(QPushButton("Forward", clicked=self.forward_chunk))
        hbox.addWidget(QPushButton("Copy", clicked=self.copy_to_clipboard))  # Adding the "Copy" button
        hbox.addWidget(self.chunk_label)
        vbox.addLayout(hbox)
        vbox.addWidget(self.output_textbox)

        # Split Button
        self.split_button = QPushButton("Split", clicked=self.split_text)
        vbox.addWidget(self.split_button)

        # Set the layout
        self.central_widget.setLayout(vbox)

        # Set default output and input text
        self.input_textbox.setPlaceholderText("Please enter the large text block to be segmented here\n")
        self.output_textbox.setPlaceholderText("Here's is where the processed output will be placed\n")

    # split_text(self)
    # self - GUI
    # Takes whatever text is in the input text box and begins making it into easy to copy and use chunks
    def split_text(self):
        # Implement the function to process the input and update the output text box
        input_text = self.input_textbox.toPlainText()

        if not input_text.strip():
            self.update_output_text("You must enter something to be splitted")
        elif len(input_text) <= self.number_allowed_characters:
            self.update_output_text("The input texts size doesn't warrant chunking")
        else:
            # Update the chunk info label
            self.chunk_label.setText("0/0")  # Update the chunk info accordingly
            self.update_chunks(input_text)
            

    # copy_to_clipboard(self)
    # self - GUI
    # Take whatever current chunk is in the output text box and copies it to the users clipboard
    def copy_to_clipboard(self):
        # Get the text from the output text box and copy it to the clipboard
        output_text = self.output_textbox.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(output_text)


    # update_chunks(self, text)
    # self - GUI
    # text - the input text boxes contents
    # Takes the entire input text and makes into chunks
    # Chunk layout is as follows
    # Instructional chunk - First chunk explains the structure to chatgpt
    # Content chunk (1 - (X - 1)) - All middle content chunks contains the data the user wants chatGPT to digest.
    # Has information telling chatGPT how to respond and to wait to digest the entire content
    # Last content chunk - Has the last chunk of content and sets up chatGPT to
    # answer a given question based on the data
    def update_chunks(self, text):
        # Instruction template, normal template, and last chunk template
        instructions = "INSTRUCTIONS: \n" \
                       "I wish to send you a large amount of content that wont fit in one message.\n" \
                       "I will be sending multiple pieces containing the content I wish to send as segments.\n" \
                       "The format is as follows\n" \
                       "[START of part {}/{}]\n" \
                       "This is the content you will be digesting\n" \
                       "[END of part {}/{}]\n" \
                       "Then just answer \"Received part {}/{}\"\n" \
                       "Once you see \"ALL PARTS SENT\" you will process all of the segments and answer the request\n"

        template = "Don't answer yet this is just another piece of segment. " \
                   "Just recieve and acknolege as \"Received part {}/{}\" and wait for the next part \n" \
                   "[START of part {}/{}]\n" \
                    "{}\n" \
                    "[END of part {}/{}]\n" \
                   "Remember don't answer yet just acknowledge you receieved the part by saying \"Received part {}/{}\""

        last_chunk_template = \
                    "[START of part {}/{}]\n" \
                    "{}\n" \
                    "[END of part {}/{}]\n" \
                   "All parts have been sent. Now please answer the given question\n"


        # Determine number of chunks dealing with
        self.end_chunk = math.ceil(len(text)/self.number_allowed_characters)
        self.start_chunk = 0

        # Set up instructional chunk
        self.chunks.append(instructions.format(0, self.end_chunk, 0, self.end_chunk, 0, self.end_chunk))
        self.update_output_text(self.chunks[0])
        # print(str(self.current_chunk) + "/" + str(self.end_chunk))
        self.update()

        # Parse through input text finding good spots to cut each chunk and then add it to the chunks list
        self.current_chunk = 1
        count = 0

        # Fill segment the content into chunks attaching each chunk as a string to the chunks list class variable
        for self.current_chunk in range(self.current_chunk, self.end_chunk + 1):
            # If last chunk then take whatever is left and using last_chunk_template attach it to the chunks list class variable
            if self.current_chunk == self.end_chunk:
                # print(str(self.current_chunk) + "/" + str(self.end_chunk))
                self.chunks.append(
                    last_chunk_template.format(self.current_chunk, self.end_chunk, text, self.current_chunk, self.end_chunk))
                break

            # Continue until each segment has been chunked and attached to the chunks list class variable
            cut_segment = False
            while not cut_segment:
                count = count + 1
                # If found a new line around the required length make that segment a chunk and attach it
                if count >= self.number_allowed_characters - self.search_offset and text[count] == '\n':
                    # print(str(self.current_chunk) + "/" + str(self.end_chunk))
                    current_segment = text[:count]
                    text = text[count:]
                    self.chunks.append(template.format(self.current_chunk, self.end_chunk, self.current_chunk, self.end_chunk, current_segment, self.current_chunk, self.end_chunk, self.current_chunk, self.end_chunk))
                    count = 0
                    cut_segment = True
                    self.current_chunk = self.current_chunk + 1


        # Set up for previewing each chunk
        self.current_chunk = 0
        self.chunk_label.setText(str(self.current_chunk) + "/" + str(self.end_chunk))

    # forward_chunk(self)
    # self - GUI
    # Move the preview forward a chunk
    def forward_chunk(self):
        if self.current_chunk >= self.end_chunk:
            self.update_input_text("AT LAST CHUNK ALREADY")
        else:
            self.current_chunk = self.current_chunk + 1
            self.update_output_text(self.chunks[self.current_chunk])

        self.chunk_label.setText(str(self.current_chunk) + "/" + str(self.end_chunk))

    # backward_chunk(self)
    # self - GUI
    # Move the preview back a chunk
    def backward_chunk(self):
        if self.current_chunk  <= self.start_chunk:
            self.update_input_text("AT FIRST CHUNK ALREADY")
        else:
            self.current_chunk = self.current_chunk - 1
            self.update_output_text(self.chunks[self.current_chunk])

        self.chunk_label.setText(str(self.current_chunk) + "/" + str(self.end_chunk))

    # update_input_text(self, text)
    # self - GUI
    # text - The string which is to be outputted to the input_textbox
    # Update the input text box
    def update_input_text(self, text):
        # Clear the output text box and set the provided text as its content
        self.input_textbox.clear()
        self.input_textbox.setPlainText(text)

    # update_output_text(self, text)
    # self - GUI
    # text - The string which is to be outputted to the output_textbox
    # Update the output text box
    def update_output_text(self, text):
        # Clear the output text box and set the provided text as its content
        self.output_textbox.clear()
        self.output_textbox.setPlainText(text)
        QApplication.processEvents()

# Main
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatGPTSplitter()
    window.show()
    sys.exit(app.exec())
