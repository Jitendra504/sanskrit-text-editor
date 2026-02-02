import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango

BASE_CONSONANTS = {
    'k': 'क', 'g': 'ग', 'c': 'च', 'j': 'ज', 't': 'त', 
    'd': 'द', 'n': 'न', 'p': 'प', 'b': 'ब', 'm': 'म', 
    'y': 'य', 'x': 'ट', 'v': 'ड', 'q': 'य', 'w': 'व', 
    'r': 'र', 'l': 'ल', 's': 'स', 'h': 'ह',
    'z': 'ऋ_BASE' 
}

GLYPH_LOGIC = {
    ('क्', 'f'): 'क्ष', ('ज्', 'f'): 'ज्ञ',
    ('क', 'f'): 'ख', ('ख', 'f'): 'क',
    ('ग', 'f'): 'घ', ('घ', 'f'): 'ग',
    ('च', 'f'): 'छ', ('छ', 'f'): 'च',
    ('ज', 'f'): 'झ', ('झ', 'f'): 'ज',
    ('त', 'f'): 'थ', ('थ', 'f'): 'त',
    ('द', 'f'): 'ध', ('ध', 'f'): 'द',
    ('प', 'f'): 'फ', ('फ', 'f'): 'प',
    ('ब', 'f'): 'भ', ('भ', 'f'): 'ब',
    ('ट', 'f'): 'ठ', ('ठ', 'f'): 'ट',
    ('ड', 'f'): 'ढ', ('ढ', 'f'): 'ड',
    ('स', 'f'): 'ष', ('ष', 'f'): 'श', ('श', 'f'): 'स',
    ('न', 'f'): 'ञ', ('ञ', 'f'): 'ण', ('ण', 'f'): 'ङ', ('ङ', 'f'): 'न',

    # Swar and Matra
    (None, 'a'): 'अ', ('अ', 'a'): 'आ',
    (None, 'i'): 'इ', ('इ', 'i'): 'ई',
    (None, 'u'): 'उ', ('उ', 'u'): 'ऊ',
    (None, 'e'): 'ए', ('ए', 'i'): 'ऐ',
    (None, 'o'): 'ओ', ('ओ', 'u'): 'औ',
    (None, 'z'): 'ऋ', ('ऋ', 'z'): 'ॠ',
    ('CONSONANT', 'a'): 'ा', ('ा', 'a'): 'ा',
    ('CONSONANT', 'i'): 'ि', ('ि', 'i'): 'ी',
    ('CONSONANT', 'u'): 'ु', ('ु', 'u'): 'ू',
    ('CONSONANT', 'e'): 'े', ('े', 'i'): 'ै',
    ('CONSONANT', 'o'): 'ो', ('ो', 'u'): 'ौ',
    ('CONSONANT', 'z'): 'ृ', ('ृ', 'z'): 'ॄ',
    ('CONSONANT', 'q'): '्', 
}

MATRAS = {'ा', 'ि', 'ी', 'ु', 'ू', 'े', 'ै', 'ो', 'ौ', 'ृ', 'ॄ', '्'}

class ShiftSwarSanskritEditor(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Sanskrit Bare-Metal (Shift=Swar)")
        self.set_default_size(700, 450)
        self.textview = Gtk.TextView()
        self.textview.set_name("sanskrit_view")
        
        css = b"#sanskrit_view { font-family: 'Lohit Devanagari'; font-size: 28pt; }"
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        self.add(self.textview)
        self.textview.connect("key-press-event", self.on_key_press)

    def on_key_press(self, widget, event):
        keyval = event.keyval
        keyname = Gdk.keyval_name(keyval)
        buf = self.textview.get_buffer()
        
        # Shift key check
        is_shift = event.state & Gdk.ModifierType.SHIFT_MASK

        if keyname == "semicolon": buf.insert_at_cursor("ः"); return True
        if keyname == "period": buf.insert_at_cursor("ं"); return True
        if keyname == "comma": buf.insert_at_cursor("।"); return True
        if len(keyname) > 1 and keyname != "space": return False
        
        char = chr(Gdk.keyval_to_unicode(keyval)).lower()
        cursor = buf.get_iter_at_mark(buf.get_insert())
        prev = ""
        if cursor.get_offset() > 0:
            i1 = cursor.copy(); i1.backward_char()
            prev = buf.get_text(i1, cursor, True)

        # --- RULE: Shift + Key = Forced Swar ---
        if is_shift and char in 'aiueoz':
            if (None, char) in GLYPH_LOGIC:
                buf.insert_at_cursor(GLYPH_LOGIC[(None, char)])
                return True

        # 1. TRANSFORMATION CYCLE
        if (prev, char) in GLYPH_LOGIC:
            buf.delete(i1, cursor)
            buf.insert_at_cursor(GLYPH_LOGIC[(prev, char)])
            return True

        # 2. NORMAL SWAR FALLBACK & MATRA
        if char in 'aiueozq':
            if prev in MATRAS:
                if (None, char) in GLYPH_LOGIC:
                    buf.insert_at_cursor(GLYPH_LOGIC[(None, char)])
                    return True
                elif char == 'q': buf.insert_at_cursor('्'); return True
            
            is_prev_cons = prev in BASE_CONSONANTS.values() or prev in GLYPH_LOGIC.values()
            if is_prev_cons:
                if ('CONSONANT', char) in GLYPH_LOGIC:
                    buf.insert_at_cursor(GLYPH_LOGIC[('CONSONANT', char)])
                    return True

        # 3. BASE ENTRIES
        if char in BASE_CONSONANTS:
            if char == 'z': buf.insert_at_cursor(GLYPH_LOGIC[(None, 'z')])
            else: buf.insert_at_cursor(BASE_CONSONANTS[char])
            return True
            
        if (None, char) in GLYPH_LOGIC:
            buf.insert_at_cursor(GLYPH_LOGIC[(None, char)])
            return True

        return False

if __name__ == "__main__":
    win = ShiftSwarSanskritEditor()
    win.connect("destroy", Gtk.main_quit); win.show_all(); Gtk.main()
