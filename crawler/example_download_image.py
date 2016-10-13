# example of how to get an image by its URL
import urllib

def download_photo(img_url, img_name):
    try:
        content = urllib.urlopen(img_url)
        if content.headers.maintype == 'image':
            fimage = file(img_name, 'wb')
            fimage.write(content.read())
            fimage.close()
            content.close()
        else:
            print 'content header is ', content.headers.maintype
            return False
    except:
        print 'Get an except when download photo.' 
        return False

    return True


if __name__ == '__main__':
    img_url = 'http://www.zj.gov.cn/picture/0/1212221511160576775.jpg'
    img_name = 'liqiang.jpg'
    download_photo(img_url, img_name)
