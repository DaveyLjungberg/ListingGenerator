from PIL import Image, ImageDraw

def create_image(filename, color):
    img = Image.new('RGB', (100, 100), color=color)
    d = ImageDraw.Draw(img)
    d.text((10, 10), filename, fill=(255, 255, 255))
    img.save(filename)

create_image('test_image_1.jpg', 'red')
create_image('test_image_2.jpg', 'blue')
