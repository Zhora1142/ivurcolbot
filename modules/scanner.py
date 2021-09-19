from zeep import Client


class Scanner:
    def __init__(self, login, lic):
        self.login = login
        self.licence = lic
        self.errorMessage = None

    def scan(self):
        client = Client('http://www.ocrwebservice.com/services/OCRWebService.asmx?WSDL')
        image = {
            'fileName': 'files/file.jpg',
            'fileData': open('files/file.jpg', 'rb').read()
        }
        settings = {
            'ocrLanguages': 'RUSSIAN',
            'outputDocumentFormat': 'XLSX',
            'convertToBW': 'true',
            'getOCRText': 'false',
            'createOutputDocument': 'true',
            'multiPageDoc': 'false',
            'ocrWords': 'false',
            'Reserved': ''
        }

        result = client.service.OCRWebServiceRecognize(user_name=self.login, license_code=self.licence,
                                                       OCRWSInputImage=image, OCRWSSetting=settings)

        if result.errorMessage:
            self.errorMessage = result.errorMessage
        else:
            with open(f'files/{result.fileName}', 'wb') as file:
                file.write(result.fileData)
                file.close()
