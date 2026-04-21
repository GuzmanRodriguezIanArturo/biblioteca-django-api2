from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend

from .throttles import BurstRateThrottle
from .external_services import GoogleBooksAPI
from .models import Categoria, Autor, Libro, Prestamo
from .serializers import (
    CategoriaSerializer, AutorSerializer, 
    LibroSerializer, PrestamoSerializer
)


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'fecha_creacion']
    ordering = ['nombre']


class AutorViewSet(viewsets.ModelViewSet):
    
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['pais_origen']
    search_fields = ['nombre', 'apellido', 'biografia']
    ordering_fields = ['apellido', 'nombre', 'fecha_creacion']
    ordering = ['apellido', 'nombre']
    
    @action(detail=True, methods=['get'])
    def libros(self, request, pk=None):
        autor = self.get_object()
        libros = autor.libros.filter(activo=True)
        serializer = LibroSerializer(libros, many=True)
        return Response(serializer.data)


class LibroViewSet(viewsets.ModelViewSet):
    
    queryset = Libro.objects.filter(activo=True).select_related('autor', 'categoria')
    serializer_class = LibroSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'categoria', 'autor']
    search_fields = ['titulo', 'isbn', 'descripcion']
    ordering_fields = ['titulo', 'precio', 'fecha_publicacion', 'valoracion']
    ordering = ['-fecha_creacion']
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        libros = self.queryset.filter(
            estado=Libro.DISPONIBLE,
            stock__gt=0
        )
        serializer = self.get_serializer(libros, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def actualizar_stock(self, request, pk=None):
        libro = self.get_object()
        cantidad = request.data.get('cantidad', 0)
        
        try:
            cantidad = int(cantidad)
        except (ValueError, TypeError):
            return Response(
                {'error': 'La cantidad debe ser un número entero'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        libro.actualizar_stock(cantidad)
        serializer = self.get_serializer(libro)
        return Response(serializer.data)


class PrestamoViewSet(viewsets.ModelViewSet):
    
    queryset = Prestamo.objects.all().select_related('libro', 'usuario')
    serializer_class = PrestamoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['estado', 'usuario']
    ordering_fields = ['fecha_prestamo', 'fecha_devolucion_esperada']
    ordering = ['-fecha_prestamo']
    
    def perform_create(self, serializer):
        prestamo = serializer.save(usuario=self.request.user)
        prestamo.libro.actualizar_stock(-1)
    
    @action(detail=True, methods=['post'])
    def devolver(self, request, pk=None):
        from django.utils import timezone
        
        prestamo = self.get_object()
        
        if prestamo.estado == Prestamo.DEVUELTO:
            return Response(
                {'error': 'Este préstamo ya fue devuelto'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        prestamo.fecha_devolucion_real = timezone.now()
        prestamo.estado = Prestamo.DEVUELTO
        prestamo.save()
        
        prestamo.libro.actualizar_stock(1)
        
        serializer = self.get_serializer(prestamo)
        return Response(serializer.data)
    
    # ✅ CORREGIDO: antes usaba @api_view (incorrecto)
    @action(detail=False, methods=['get'], throttle_classes=[BurstRateThrottle])
    def api_intensiva(self, request):
        return Response({'data': 'información'})
    
    # ✅ CORREGIDO: antes usaba @api_view y @permission_classes (incorrecto)
    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def importar_desde_google_books(self, request):
        isbn = request.data.get('isbn')
        
        if not isbn:
            return Response({
                'error': 'ISBN es requerido'
            }, status=400)
        
        data = GoogleBooksAPI.buscar_libro(isbn)
        
        if not data:
            return Response({
                'error': 'Libro no encontrado en Google Books'
            }, status=404)
        
        return Response({
            'mensaje': 'Libro encontrado',
            'data': data
        }, status=200)