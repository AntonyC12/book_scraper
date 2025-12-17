# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pandas as pd
from collections import Counter

class BookScraperPipeline:
    def __init__(self):
        self.books_data = []
    
    def process_item(self, item, spider):
        self.books_data.append(dict(item))
        return item
    
    def close_spider(self, spider):
        if not self.books_data:
            print("No se recolectaron datos.")
            return
        
        # Crear DataFrame
        df = pd.DataFrame(self.books_data)
        
        # 1. EXPORTAR A EXCEL
        excel_filename = "books_analysis.xlsx"
        
        # Crear un writer de Excel con múltiples hojas
        with pd.ExcelWriter(excel_filename, engine='openpyxl') as writer:
            # Hoja 1: Todos los datos
            df.to_excel(writer, sheet_name='Todos los Libros', index=False)
            
            # Hoja 2: Libros más caros (orden descendente)
            expensive_books = df.sort_values('price', ascending=False)
            expensive_books.to_excel(writer, sheet_name='Libros Más Caros', index=False)
            
            # Hoja 3: Mejores calificaciones (rating 4-5)
            best_rated = df[df['rating'] >= 4].sort_values('rating', ascending=False)
            best_rated.to_excel(writer, sheet_name='Mejores Calificados', index=False)
            
            # Hoja 4: Peores calificaciones (rating 1-2)
            worst_rated = df[df['rating'] <= 2].sort_values('rating', ascending=True)
            worst_rated.to_excel(writer, sheet_name='Peores Calificados', index=False)
            
            # Hoja 5: Top 5 autores por cantidad de libros
            author_counts = df['author'].value_counts().head(5)
            author_df = pd.DataFrame({
                'Autor': author_counts.index,
                'Cantidad de Libros': author_counts.values
            })
            author_df.to_excel(writer, sheet_name='Top 5 Autores', index=False)
            
            # Hoja 6: Estadísticas resumidas
            stats = {
                'Métrica': [
                    'Total de Libros', 
                    'Precio Promedio', 
                    'Rating Promedio',
                    'Libros en Stock',
                    'Libros sin Stock',
                    'Año Promedio'
                ],
                'Valor': [
                    len(df),
                    f"£{df['price'].mean():.2f}",
                    f"{df['rating'].mean():.1f} estrellas",
                    df['in_stock'].sum(),
                    len(df) - df['in_stock'].sum(),
                    int(df['year'].mean())
                ]
            }
            stats_df = pd.DataFrame(stats)
            stats_df.to_excel(writer, sheet_name='Estadísticas', index=False)
        
        print(f"[SUCCESS] Datos exportados a '{excel_filename}'")
        
        # 2. GENERAR REPORTE DE TEXTO
        self.generate_text_report(df)
    
    def generate_text_report(self, df):
        """Genera un reporte detallado en formato texto."""
        with open("analysis_report.txt", "w", encoding="utf-8") as f:
            f.write("="*60 + "\n")
            f.write("ANÁLISIS COMPLETO DE BOOKS.TOSCRAPE.COM\n")
            f.write("="*60 + "\n\n")
            
            f.write(f"Total de libros analizados: {len(df)}\n\n")
            
            # 1. LIBROS MÁS CAROS (Top 10)
            f.write("="*60 + "\n")
            f.write("TOP 10 LIBROS MÁS CAROS\n")
            f.write("="*60 + "\n")
            expensive = df.sort_values('price', ascending=False).head(10)
            for idx, row in expensive.iterrows():
                f.write(f"{row['title']} - £{row['price']:.2f} (Rating: {row['rating']}/5)\n")
            
            # 2. MEJORES CALIFICACIONES (Top 10)
            f.write("\n" + "="*60 + "\n")
            f.write("TOP 10 MEJORES CALIFICACIONES (5 estrellas)\n")
            f.write("="*60 + "\n")
            best = df[df['rating'] == 5].sort_values('price', ascending=False).head(10)
            if len(best) > 0:
                for idx, row in best.iterrows():
                    f.write(f"{row['title']} - £{row['price']:.2f} - {row['author']}\n")
            else:
                f.write("No hay libros con 5 estrellas\n")
            
            # 3. PEORES CALIFICACIONES (Top 10)
            f.write("\n" + "="*60 + "\n")
            f.write("TOP 10 PEORES CALIFICACIONES (1-2 estrellas)\n")
            f.write("="*60 + "\n")
            worst = df[df['rating'] <= 2].sort_values('rating').head(10)
            if len(worst) > 0:
                for idx, row in worst.iterrows():
                    f.write(f"{row['title']} - £{row['price']:.2f} - Rating: {row['rating']}/5\n")
            else:
                f.write("No hay libros con baja calificación\n")
            
            # 4. TOP 5 AUTORES
            f.write("\n" + "="*60 + "\n")
            f.write("TOP 5 AUTORES CON MÁS LIBROS\n")
            f.write("="*60 + "\n")
            author_counts = df['author'].value_counts().head(5)
            for author, count in author_counts.items():
                f.write(f"{author}: {count} libros\n")
            
            # 5. ESTADÍSTICAS ADICIONALES
            f.write("\n" + "="*60 + "\n")
            f.write("ESTADÍSTICAS ADICIONALES\n")
            f.write("="*60 + "\n")
            f.write(f"Precio más alto: £{df['price'].max():.2f}\n")
            f.write(f"Precio más bajo: £{df['price'].min():.2f}\n")
            f.write(f"Precio promedio: £{df['price'].mean():.2f}\n")
            f.write(f"Rating promedio: {df['rating'].mean():.1f}/5\n")
            f.write(f"Libros en stock: {df['in_stock'].sum()} ({df['in_stock'].mean()*100:.1f}%)\n")
            f.write(f"Libros sin stock: {len(df) - df['in_stock'].sum()}\n")
            
            # 6. DISTRIBUCIÓN POR RATING
            f.write("\n" + "="*60 + "\n")
            f.write("DISTRIBUCIÓN POR CALIFICACIÓN\n")
            f.write("="*60 + "\n")
            for rating in range(1, 6):
                count = len(df[df['rating'] == rating])
                percentage = (count / len(df)) * 100
                stars = "★" * rating + "☆" * (5 - rating)
                f.write(f"{stars}: {count} libros ({percentage:.1f}%)\n")
        
        print("[SUCCESS] Reporte de análisis generado en 'analysis_report.txt'")