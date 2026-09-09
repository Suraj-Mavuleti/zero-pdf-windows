import sys
import gi
import os
import json
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

CONFIG_DIR = os.path.expanduser("~/.config/zero-pdf")
RECENT_FILE = os.path.join(CONFIG_DIR, "recent.json")

class ZeroPDF(Gtk.Window):
    def __init__(self):
        super().__init__(title="Zero PDF - Ultimate Studio")
        self.set_default_size(1200, 800)
        
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self.recent_files = self.load_recent()
        
        self.header = Gtk.HeaderBar()
        self.header.set_show_close_button(True)
        self.header.props.title = ""
        self.header.get_style_context().add_class("hidden-header")
        self.set_titlebar(self.header)
        
        self.setup_css()
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(main_box)
        
        # ================= SIDEBAR =================
        self.sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.sidebar.set_size_request(280, -1)
        self.sidebar.get_style_context().add_class("sidebar")
        main_box.pack_start(self.sidebar, False, False, 0)
        
        logo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        logo = Gtk.Label(label="Z E R O P D F")
        logo.get_style_context().add_class("sidebar-logo")
        logo_box.pack_start(logo, True, True, 0)
        self.sidebar.pack_start(logo_box, False, False, 20)
        
        self.btn_open = Gtk.Button(label="📄 Open PDF")
        self.btn_open.get_style_context().add_class("action-btn")
        self.btn_open.connect("clicked", self.on_open_pdf)
        self.sidebar.pack_start(self.btn_open, False, False, 10)
        
        lbl_recent = Gtk.Label(label="RECENT FILES")
        lbl_recent.get_style_context().add_class("section-label")
        lbl_recent.set_halign(Gtk.Align.START)
        lbl_recent.set_margin_start(20)
        lbl_recent.set_margin_top(20)
        self.sidebar.pack_start(lbl_recent, False, False, 10)
        
        self.recent_list = Gtk.ListBox()
        self.recent_list.get_style_context().add_class("transparent-list")
        self.update_recent_ui()
        self.sidebar.pack_start(self.recent_list, False, False, 0)
        
        # Bottom tools
        tools_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        tools_box.set_margin_start(15)
        tools_box.set_margin_end(15)
        tools_box.set_margin_bottom(20)
        
        self.btn_convert = Gtk.Button(label="🔄 Convert Tools")
        self.btn_convert.get_style_context().add_class("nav-btn")
        self.btn_convert.connect("clicked", self.show_converter)
        tools_box.pack_start(self.btn_convert, False, False, 0)
        
        self.btn_ocr = Gtk.Button(label="👁️ OCR Engine")
        self.btn_ocr.get_style_context().add_class("nav-btn")
        self.btn_ocr.connect("clicked", self.show_ocr)
        tools_box.pack_start(self.btn_ocr, False, False, 0)
        
        self.sidebar.pack_end(tools_box, False, False, 0)
        
        # ================= MAIN WORKSPACE =================
        self.workspace = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.workspace.get_style_context().add_class("workspace")
        main_box.pack_start(self.workspace, True, True, 0)
        
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.workspace.pack_start(self.stack, True, True, 0)
        
        # View 1: Empty / Welcome
        welcome_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        welcome_box.set_valign(Gtk.Align.CENTER)
        welcome_box.set_halign(Gtk.Align.CENTER)
        w_lbl = Gtk.Label(label="Ultimate PDF Studio")
        w_lbl.get_style_context().add_class("welcome-title")
        w_sub = Gtk.Label(label="Open a PDF to start editing or use conversion tools.")
        w_sub.get_style_context().add_class("welcome-sub")
        welcome_box.pack_start(w_lbl, False, False, 10)
        welcome_box.pack_start(w_sub, False, False, 0)
        self.stack.add_named(welcome_box, "welcome")
        
        # View 2: Converter Dashboard (Glassmorphism Slide-down simulation)
        self.converter_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.converter_box.set_valign(Gtk.Align.CENTER)
        self.converter_box.set_halign(Gtk.Align.CENTER)
        c_title = Gtk.Label(label="Conversion Matrix")
        c_title.get_style_context().add_class("welcome-title")
        self.converter_box.pack_start(c_title, False, False, 20)
        
        grid = Gtk.Grid(column_spacing=20, row_spacing=20)
        grid.attach(self.make_tool_card("📝 Word to PDF"), 0, 0, 1, 1)
        grid.attach(self.make_tool_card("🖼️ Pic to PDF"), 1, 0, 1, 1)
        grid.attach(self.make_tool_card("📊 Excel to PDF"), 0, 1, 1, 1)
        grid.attach(self.make_tool_card("📦 PDF to Word/Images"), 1, 1, 1, 1)
        self.converter_box.pack_start(grid, False, False, 0)
        self.stack.add_named(self.converter_box, "converter")
        
        # View 3: OCR Dashboard
        self.ocr_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.ocr_box.set_valign(Gtk.Align.CENTER)
        self.ocr_box.set_halign(Gtk.Align.CENTER)
        o_title = Gtk.Label(label="Deep OCR Engine")
        o_title.get_style_context().add_class("welcome-title")
        o_sub = Gtk.Label(label="Extract text and make scanned documents editable.")
        o_sub.get_style_context().add_class("welcome-sub")
        self.ocr_box.pack_start(o_title, False, False, 10)
        self.ocr_box.pack_start(o_sub, False, False, 20)
        btn_run_ocr = Gtk.Button(label="Select Scanned PDF")
        btn_run_ocr.get_style_context().add_class("action-btn")
        self.ocr_box.pack_start(btn_run_ocr, False, False, 0)
        self.stack.add_named(self.ocr_box, "ocr")
        
        self.stack.set_visible_child_name("welcome")
        
    def make_tool_card(self, text):
        btn = Gtk.Button(label=text)
        btn.get_style_context().add_class("tool-card")
        btn.set_size_request(200, 120)
        return btn

    def load_recent(self):
        try:
            if os.path.exists(RECENT_FILE):
                with open(RECENT_FILE, "r") as f: return json.load(f)
        except: pass
        return []

    def save_recent(self):
        os.makedirs(os.path.dirname(RECENT_FILE), exist_ok=True)
        with open(RECENT_FILE, "w") as f: json.dump(self.recent_files[:10], f)

    def update_recent_ui(self):
        for child in self.recent_list.get_children():
            self.recent_list.remove(child)
        for path in self.recent_files:
            row = Gtk.ListBoxRow()
            row.get_style_context().add_class("recent-row")
            lbl = Gtk.Label(label=os.path.basename(path))
            lbl.set_halign(Gtk.Align.START)
            lbl.set_margin_start(15)
            lbl.set_margin_top(10)
            lbl.set_margin_bottom(10)
            row.add(lbl)
            self.recent_list.add(row)
        self.recent_list.show_all()

    def on_open_pdf(self, widget):
        dialog = Gtk.FileChooserDialog(title="Open PDF", parent=self, action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        filter_pdf = Gtk.FileFilter()
        filter_pdf.set_name("PDF files")
        filter_pdf.add_pattern("*.pdf")
        dialog.add_filter(filter_pdf)
        
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            if filename not in self.recent_files:
                self.recent_files.insert(0, filename)
                self.save_recent()
                self.update_recent_ui()
            # Simulation of opening pdf
            self.stack.set_visible_child_name("welcome")
            print("Opened PDF:", filename)
        dialog.destroy()

    def show_converter(self, widget):
        self.stack.set_visible_child_name("converter")

    def show_ocr(self, widget):
        self.stack.set_visible_child_name("ocr")

    def setup_css(self):
        css = b'''
            window { background-color: #030305; }
            .hidden-header { background: #030305; min-height: 0px; padding: 0px; border: none; box-shadow: none; }
            .sidebar { background-color: rgba(8, 10, 16, 0.95); border-right: 1px solid rgba(255, 255, 255, 0.05); }
            .sidebar-logo { color: #FFFFFF; font-size: 22px; font-weight: 900; letter-spacing: 5px; text-shadow: 0 0 15px rgba(255,0,85,0.6); }
            .action-btn { background: linear-gradient(45deg, #FF0055, #FF5500); color: white; border-radius: 20px; font-weight: bold; padding: 12px; margin: 0 15px; border: none; box-shadow: 0 5px 15px rgba(255,0,85,0.4); transition: all 0.3s; }
            .action-btn:hover { box-shadow: 0 8px 25px rgba(255,0,85,0.6); }
            .section-label { color: #4A5568; font-size: 11px; font-weight: 900; letter-spacing: 2px; }
            .transparent-list { background: transparent; }
            .recent-row { background: transparent; color: #8B94A5; font-weight: bold; font-size: 13px; border-radius: 8px; margin: 2px 10px; border: 1px solid transparent; }
            .recent-row:hover { background: rgba(255, 255, 255, 0.05); color: #FFFFFF; }
            .nav-btn { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); color: #8B94A5; border-radius: 12px; padding: 12px; font-weight: bold; font-size: 14px; transition: all 0.2s ease; }
            .nav-btn:hover { background: rgba(255,0,85,0.1); color: #FF0055; border: 1px solid #FF0055; box-shadow: 0 0 15px rgba(255,0,85,0.2); }
            .workspace { background: radial-gradient(circle at center, #10141E, #030305); }
            .welcome-title { font-size: 42px; font-weight: bold; color: #FFFFFF; text-shadow: 0 5px 20px rgba(0,0,0,0.5); margin-bottom: 10px; }
            .welcome-sub { font-size: 18px; color: #8B94A5; }
            .tool-card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 20px; color: #FFFFFF; font-size: 16px; font-weight: bold; transition: all 0.3s ease; box-shadow: 0 10px 30px rgba(0,0,0,0.3); backdrop-filter: blur(10px); }
            .tool-card:hover { transform: translateY(-5px); background: rgba(255,0,85,0.1); border: 1px solid #FF0055; box-shadow: 0 15px 40px rgba(255,0,85,0.3); }
        '''
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

if __name__ == "__main__":
    win = ZeroPDF()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
