import React, { useState, useEffect } from 'react';
import {
  Box,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Typography,
  Alert,
  Paper,
  Button,
  CircularProgress,
  Snackbar
} from '@mui/material';
import { getSystemConfig, setAIModel } from '../services/configService';

interface AIModelSelectorProps {
  onModelChange?: (model: string) => void;
}

const AIModelSelector: React.FC<AIModelSelectorProps> = ({ onModelChange }) => {
  const [currentModel, setCurrentModel] = useState<'clip' | 'opencv_dnn' | 'opencv_yolo'>('clip');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Cargar la configuración actual al inicio
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        setLoading(true);
        const config = await getSystemConfig();
        setCurrentModel(config.current_settings.ai_model);
        setError(null);
      } catch (err) {
        setError('Error al cargar la configuración actual');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchConfig();
  }, []);

  // Manejar cambio de modelo
  const handleModelChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentModel(event.target.value as 'clip' | 'opencv_dnn');
  };

  // Guardar la configuración
  const saveConfig = async () => {
    try {
      setSaving(true);
      setError(null);
      
      await setAIModel(currentModel);
      
      // Determinar mensaje según el modelo seleccionado
      let modelDisplayName = '';
      if (currentModel === 'clip') {
        modelDisplayName = 'CLIP';
      } else if (currentModel === 'opencv_dnn') {
        modelDisplayName = 'OpenCV+DNN';
      } else if (currentModel === 'opencv_yolo') {
        modelDisplayName = 'OpenCV+YOLO';
      }
      
      setSuccess(`Modelo cambiado a ${modelDisplayName}`);
      
      if (onModelChange) {
        onModelChange(currentModel);
      }
    } catch (err) {
      setError('Error al cambiar el modelo de IA');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSuccess(null);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" m={2}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Configuración del Modelo de IA
      </Typography>
      
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      
      <FormControl component="fieldset">
        <FormLabel component="legend">Seleccione el modelo a utilizar para clasificar imágenes:</FormLabel>
        <RadioGroup value={currentModel} onChange={handleModelChange}>
          <FormControlLabel 
            value="clip" 
            control={<Radio />} 
            label="CLIP (mayor precisión en la clasificación de eventos)" 
          />
          <FormControlLabel 
            value="opencv_dnn" 
            control={<Radio />} 
            label="OpenCV + DNN (más rápido, menor uso de recursos)" 
          />
          <FormControlLabel 
            value="opencv_yolo" 
            control={<Radio />} 
            label="OpenCV + YOLO (detección de objetos avanzada)" 
          />
        </RadioGroup>
      </FormControl>
      
      <Box mt={2}>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={saveConfig} 
          disabled={saving}
          startIcon={saving ? <CircularProgress size={20} /> : null}
        >
          {saving ? 'Guardando...' : 'Guardar cambios'}
        </Button>
      </Box>
      
      <Snackbar
        open={success !== null}
        autoHideDuration={5000}
        onClose={handleCloseSnackbar}
        message={success}
      />
      
      <Box mt={2}>
        <Typography variant="body2" color="textSecondary">
          <strong>CLIP:</strong> Modelo de OpenAI que ofrece alta precisión en la detección de eventos en imágenes, 
          pero requiere más recursos computacionales.
        </Typography>
        <Typography variant="body2" color="textSecondary" mt={1}>
          <strong>OpenCV + DNN:</strong> Utiliza redes neuronales preentrenadas (ResNet-50) para detectar objetos 
          en imágenes con menor uso de recursos, aunque con menor precisión para eventos específicos.
        </Typography>
        <Typography variant="body2" color="textSecondary" mt={1}>
          <strong>OpenCV + YOLO:</strong> Implementa el modelo YOLOv4 para detección de objetos en tiempo real, 
          ofreciendo un balance entre precisión y velocidad. Ideal para identificar múltiples objetos en la imagen.
        </Typography>
      </Box>
    </Paper>
  );
};

export default AIModelSelector;
