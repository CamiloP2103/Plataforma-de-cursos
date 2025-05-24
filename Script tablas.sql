CREATE TABLE `archivos_curso` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre_archivo` varchar(256) DEFAULT NULL,
  `ruta_archivo` varchar(512) DEFAULT NULL,
  `curso_id` int DEFAULT NULL,
  `ruta_podcast` varchar(512) DEFAULT NULL,
  `transcripcion` text,
  PRIMARY KEY (`id`),
  KEY `curso_id` (`curso_id`),
  CONSTRAINT `archivos_curso_ibfk_1` FOREIGN KEY (`curso_id`) REFERENCES `cursos` (`id_curso`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `curso_estudiante` (
  `usuario_id` int NOT NULL,
  `curso_id` int NOT NULL,
  PRIMARY KEY (`usuario_id`,`curso_id`),
  KEY `curso_id` (`curso_id`),
  CONSTRAINT `curso_estudiante_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usr`) ON DELETE CASCADE,
  CONSTRAINT `curso_estudiante_ibfk_2` FOREIGN KEY (`curso_id`) REFERENCES `cursos` (`id_curso`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `cursos` (
  `id_curso` int NOT NULL AUTO_INCREMENT,
  `nombre_curso` varchar(255) DEFAULT NULL,
  `descripcion` varchar(255) DEFAULT NULL,
  `fecha_creacion` datetime DEFAULT NULL,
  `profesor_id` int DEFAULT NULL,
  PRIMARY KEY (`id_curso`),
  KEY `fk_profesor` (`profesor_id`),
  CONSTRAINT `fk_profesor` FOREIGN KEY (`profesor_id`) REFERENCES `usuarios` (`id_usr`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `usuarios` (
  `id_usr` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(256) DEFAULT NULL,
  `Contraseña` varchar(256) DEFAULT NULL,
  `Tipo_usr` int DEFAULT NULL,
  `estado` bit(1) DEFAULT NULL,
  PRIMARY KEY (`id_usr`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



