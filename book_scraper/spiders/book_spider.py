import scrapy
import re
from datetime import datetime
from book_scraper.items import BookItem

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]
    
    def parse(self, response):
        """Parsea la página principal y sigue los enlaces a categorías y páginas."""
        # Primero, extraer libros de la página actual
        books = response.css('article.product_pod')
        for book in books:
            book_url = book.css('h3 a::attr(href)').get()
            if book_url:
                yield response.follow(book_url, self.parse_book)
        
        # Paginación
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
    
    def parse_book(self, response):
        """Extrae los detalles de un libro individual."""
        item = BookItem()
        
        # Título
        item['title'] = response.css('div.product_main h1::text').get()
        
        # Autor
        author = response.xpath('//th[text()="Author"]/following-sibling::td/a/text()').get()
        item['author'] = author.strip() if author else "Unknown"
        
        # Precio
        price_text = response.css('p.price_color::text').get()
        if price_text:
            # Extraer solo números y punto decimal
            price = re.search(r'[\d.]+', price_text)
            item['price'] = float(price.group()) if price else 0.0
        else:
            item['price'] = 0.0
        
        # Stock (disponibilidad)
        stock_text = response.xpath('//th[text()="Availability"]/following-sibling::td/text()').get()
        if stock_text:
            # Extraer número del texto de stock
            stock_match = re.search(r'(\d+)', stock_text)
            item['stock'] = int(stock_match.group(1)) if stock_match else 0
            item['in_stock'] = item['stock'] > 0
        else:
            item['stock'] = 0
            item['in_stock'] = False
        
        # Calificación (rating)
        rating_class = response.css('p.star-rating::attr(class)').get()
        if rating_class:
            # Mapear clase a número (One=1, Two=2, etc.)
            rating_map = {
                'One': 1, 'Two': 2, 'Three': 3, 
                'Four': 4, 'Five': 5
            }
            rating_text = rating_class.split()[-1]
            item['rating'] = rating_map.get(rating_text, 0)
        else:
            item['rating'] = 0
        
        # Año de publicación (intentamos extraer de la descripción o UPC)
        # Nota: Esta página no tiene año explícito, así que usaremos un aproximado
        description = response.xpath('//div[@id="product_description"]/following-sibling::p/text()').get()
        if description:
            # Buscar años en la descripción
            year_match = re.search(r'\b(19|20)\d{2}\b', description)
            item['year'] = int(year_match.group()) if year_match else 2000
        else:
            item['year'] = 2000  # Valor por defecto
        
        # Categoría
        item['category'] = response.css('ul.breadcrumb li:nth-last-child(2) a::text').get()
        
        # URL del libro
        item['url'] = response.url
        
        yield item