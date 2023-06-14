class Element:
    x = 0
    y = 0

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def get_pos(self):
        return (self.x, self.y)

    def draw(self):
        pass

class Text(Element):
    content = False
    font = False

    def __init__(self, content, font, x=0, y=0):
        super().__init__(x, y)
        self.content = content
        self.font = font

    def draw(self, screen):
        text = self.font.render(self.content, True, (0,0,0))
        screen.blit(text, (self.x, self.y))

    def set_content(self, content):
        self.content = content

    def get_content(self):
        return self.content

    def set_font(self, font):
        self.font = font

    def get_font(self):
        return self.font
