# Worklog - Proyecto Microservicios No Monolíticos

## Resumen del Proyecto

Sistema de microservicios para gestión de campañas, tracking de evidencias, cálculo de comisiones y procesamientos de pagos, implementado con arquitectura dirigida por eventos.

---

## Actividades por Miembro del Equipo

### 👨‍💻 **Juan Motta** (ja.lopezm123@uniandes.edu.co)

• Implementó generador de tokens JWT para testing
• Agregó scripts de desarrollo local y documentación
• Mejoró arquitectura dirigida por eventos del BFF
• Implementó handlers de tracking y esquemas Avro
• Creó suite completa de testing y herramientas de debugging
• Desarrolló guías de configuración y scripts de automatización
• Configuración inicial del proyecto con Docker
• Implementó arquitectura base de eventos con Pulsar
• Estableció fundación arquitectónica del sistema

---

### 👨‍💻 **Martin Galvan Castro** (md.galvan@uniandes.edu.co)

• Implementó microservicio BFF completo desde cero
• Desarrolló API con routers para campaigns, evidence y payments
• Creó sistema de autenticación JWT y handlers de comandos
• Configuró infraestructura de mensajería Pulsar
• Inicializó servicio de comisiones con scripts y tests
• Implementó command bus y arquitectura de eventos

---

### 👨‍💻 **Andrés Duque** (a.duquec@uniandes.edu.co)

• Configuró DataStax Astra Streaming completo
• Implementó Dockerfiles y scripts de verificación
• Desarrolló documentación de setup y troubleshooting
• Creó configuraciones de entorno y deployment
• Estableció conexiones y tests de conectividad
• Implementó scripts de automatización de servicios

---

### 👨‍💻 **Diego Fonseca** (da.fonseca@uniandes.edu.co)

• Implementó funcionalidad completa de cálculo de comisiones
• Desarrolló API endpoints y command handling
• Creó aggregates de dominio y eventos de negocio
• Implementó repositorios y modelos de datos
• Configuró contenedor de dependencias

---

## Resumen del Proyecto

### Servicios Implementados

• **BFF Service** - Backend for Frontend
• **Campaign Service** - Gestión de campañas  
• **Commission Service** - Cálculo de comisiones
• **Payment Service** - Procesamiento de pagos
• **Tracking Service** - Seguimiento de evidencias

### Tecnologías Clave

• Apache Pulsar para mensajería
• Docker & Docker Compose
• JWT Authentication
• Avro Schemas
• DataStax Astra Streaming
• Event-Driven Architecture
