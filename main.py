import tkinter as tk
from time import sleep

from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog, messagebox
import whisper
import threading

DEFAULT_MODEL = "large-v2"
CONFIG = {
    "file_path": "",
    "result": "",
    "loading_text": "Lade Modell",
    "loading": False
}


def transcribe_file():
    """
    Transcribe an audio file using OpenAI Whisper.
    """
    CONFIG["loading"] = True

    if CONFIG["file_path"] == "":
        # show error messagebox
        messagebox.showerror("Fehler", "Keine Datei ausgewählt.")
        return

    # clear the input box
    text_box.delete("1.0", tk.END)

    loading_label.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")  # show loading label
    CONFIG["loading_text"] = "Lade Modell"
    loading_label.config(text=CONFIG["loading_text"])

    # get the selected whisper model from the dropdown menu
    try:
        model = model_var.get()
        model = whisper.load_model(model)
    except Exception as e:
        print(e)
        messagebox.showerror("Fehler", "Modell konnte nicht geladen werden.")
        CONFIG["loading"] = False
        loading_label.grid_forget()  # hide loading label
        return

    CONFIG["loading_text"] = "Transkribiere Datei"
    loading_label.config(text=CONFIG["loading_text"])

    # transcribe the file
    try:
        result = model.transcribe(CONFIG["file_path"])
        CONFIG["result"] = result["text"]

        loading_label.grid_forget()  # hide loading label
    except Exception as e:
        print(e)
        messagebox.showerror("Fehler", "Datei konnte nicht transkribiert werden.")
        CONFIG["loading"] = False
        loading_label.grid_forget()  # hide loading label
        return

    # display the transcription in the text box
    text_box.insert(tk.END, CONFIG["result"])

    CONFIG["loading"] = False


def dot_dot_dot_thread():
    """
    Display a loading animation.
    """
    while CONFIG["loading"]:
        for i in range(4):
            loading_label.config(text=f"{CONFIG['loading_text']}{'.' * i}")
            sleep(0.5)


def copy_to_clipboard():
    """
    Copy the transcription to the clipboard.
    """

    if not CONFIG["result"]:
        messagebox.showerror("Fehler", "Kein Transkript vorhanden.")
        return

    text_box.clipboard_clear()
    text_box.clipboard_append(CONFIG["result"])
    text_box.update()

    messagebox.showinfo("Erfolgreich", "Transkript wurde in die Zwischenablage kopiert.")


def save_to_file():
    """
    Save the transcription to a file.
    """

    save_location = filedialog.asksaveasfilename(title="Transkript speichern", defaultextension=".txt",
                                             filetypes=(("Textdateien", "*.txt"), ("Alle Dateiarten", "*.*")))
    if not save_location:
        print("No save location selected")
        return

    with open(save_location, "w") as f:
        f.write(CONFIG["result"])

    messagebox.showinfo("Erfolgreich", "Transkript wurde gespeichert.")


def update_label(file_path):
    label.config(text=f"Ausgewählte Datei: {file_path}")
    CONFIG["file_path"] = file_path


def file_drop(event):
    """Handle file drop event."""
    update_label(event.data)


def browse_file():
    """
    Open a file browser to select a file.
    """
    file_path = filedialog.askopenfilename(title="Datei auswählen")
    if not file_path:
        return
    update_label(file_path)


def start_transcription_thread():
    threading.Thread(target=transcribe_file).start()
    threading.Thread(target=dot_dot_dot_thread).start()


if __name__ == "__main__":
    # Create the main window
    root = TkinterDnD.Tk()
    root.title("Whisper Python GUI")

    # set program icon ('icon.svg')
    root.iconphoto(True, tk.PhotoImage(file= "src/img/icon.png"))

    # Make the window accept file drops
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', file_drop)

    # Create a label and button to browse for a file
    label = tk.Label(root, text="Ziehe eine Datei hierher, oder importiere sie.")
    label.grid(row=0, column=0, columnspan=2, padx=50, pady=30, sticky="ew")

    # Create a button to browse for a file
    btn_browse = tk.Button(root, text="Importieren", command=browse_file)
    btn_browse.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    # create drop down menu with model options
    model_options = ["tiny", "base", "small", "medium", "large-v1", "large-v2"]
    model_var = tk.StringVar(root)

    # set default model (DEFAULT_MODEL)
    model_var.set(model_options[model_options.index(DEFAULT_MODEL)])
    model_menu = tk.OptionMenu(root, model_var, *model_options)
    model_menu.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

    # transcribe button
    transcribe_btn = tk.Button(root, text="Transkribieren", command=start_transcription_thread, width=15)
    transcribe_btn.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    # display transcription in text box
    text_box = tk.Text(root, height=10)
    text_box.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    # button to copy transcription to clipboard
    copy_btn = tk.Button(root, text="Kopieren", command=copy_to_clipboard)
    copy_btn.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

    # button to save transcription to file
    save_btn = tk.Button(root, text="Speichern", command=save_to_file)
    save_btn.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

    # loading label
    loading_label = tk.Label(root, text="")
    loading_label.grid_forget()

    root.mainloop()
