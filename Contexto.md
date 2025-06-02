Me gustaría el contexto para una IA desarrollar un sistema con las siguientes características:
1 – El sistema debe ser ejecutado en una maquina con Linux, más precisamente Ubuntu 24.04 Desktop.
2 – Debe estar implementado en Python, Docker y Docker Compose.
3 -Debe de tener una base de dados.
4 – Las funcionalidades que deben ser implementadas son:
	1 – Selección de archivos (fotos/videos – todas las codificaciones) (uno o múltiplos)
	2 – Deben ser extraídos dados de eses archivos a través de los siguientes métodos: metadatos incrustados, sidecar y el uso de una IA(CLIP) para el reconocimiento del tipo de evento.
	3 – Eses dados deben ser almacenados em una base de dados.
	4 – Debe ser creada una miniatura para ser visualizada en una tela web.
	5 – Un botón para excluir el archivo.
	6 – Un botón para editar los dados del archivo.
5 – La tela debe ser actualizada siempre que un evento ocurra( la selección de un nuevo archivo, la exclusión de un archivo o en la edición de un archivo).
6 – La tela web deberá tener este dibujo:  
7 – El proyecto debe ser capaz de identificar todas las dependencias necesarias y impleméntalas, tales como compilador Python, Docker, Docker compose, estructuras de directorios, etc.