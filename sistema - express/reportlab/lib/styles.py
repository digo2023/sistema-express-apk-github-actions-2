class ParagraphStyle:
    def __init__(self, name='Normal', parent=None, **kwargs):
        self.name=name
        self.parent=parent
        self.__dict__.update(kwargs)
class StyleSheet(dict):
    def add(self, style):
        self[style.name]=style
def getSampleStyleSheet():
    s=StyleSheet()
    for name in ['Title','Heading1','Heading2','Heading3','BodyText','Normal']:
        s[name]=ParagraphStyle(name=name)
    return s
