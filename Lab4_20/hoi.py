"""Модуль для обработки аудиофайлов и извлечения метаданных."""
import os
from typing import Tuple
import librosa
import numpy as np


class AudioProcessor:
    """Класс для обработки аудиофайлов и извлечения метаданных."""

    @staticmethod
    def get_min_amplitude_practical(file_path: str, threshold: float = 0.001) -> float:
        try:
            # Загружаем аудиофайл
            audio_data, sample_rate = librosa.load(file_path, sr=None, mono=True)
            
            # Вычисляем абсолютные значения амплитуд
            abs_amplitudes = np.abs(audio_data)
            
            # Игнорируем значения ниже порога шума
            amplitudes_above_threshold = abs_amplitudes[abs_amplitudes > threshold]
            
            if len(amplitudes_above_threshold) > 0:
                # Если есть значения выше порога, берем минимальное из них
                practical_min = np.min(amplitudes_above_threshold)
            else:
                # Если все значения ниже порога, берем максимальное (самое громкое)
                practical_min = np.max(abs_amplitudes)
            
            return round(practical_min, 6)
        except Exception as e:
            raise Exception(f"Ошибка при получении практической амплитуды файла {file_path}: {e}")

    @staticmethod
    def get_min_amplitude(file_path: str) -> float:
        try:
            # Загружаем аудиофайл
            audio_data, sample_rate = librosa.load(file_path, sr=None, mono=True)
            
            # Находим минимальную амплитуду по модулю
            min_amplitude_abs = np.min(np.abs(audio_data))
            
            return round(min_amplitude_abs, 8)  # Увеличиваем точность
        except Exception as e:
            raise Exception(f"Ошибка при получении амплитуды файла {file_path}: {e}")

    @staticmethod
    def get_amplitude_percentile(file_path: str, percentile: float = 1.0) -> float:
        try:
            audio_data, sample_rate = librosa.load(file_path, sr=None, mono=True)
            abs_amplitudes = np.abs(audio_data)
            
            # Вычисляем процентиль
            amplitude_percentile = np.percentile(abs_amplitudes, percentile)
            
            return round(amplitude_percentile, 8)
        except Exception as e:
            raise Exception(f"Ошибка при получении процентиля амплитуды: {e}")

    @staticmethod
    def get_amplitude_statistics(file_path: str) -> dict:
        try:
            audio_data, sample_rate = librosa.load(file_path, sr=None, mono=True)
            abs_amplitudes = np.abs(audio_data)
            
            # Основные метрики
            stats = {
                'duration': round(librosa.get_duration(y=audio_data, sr=sample_rate), 3),
                'sample_rate': sample_rate,
                'total_samples': len(audio_data),
                
                # Точные амплитудные метрики
                'min_amplitude_abs': round(np.min(abs_amplitudes), 8),
                'max_amplitude_abs': round(np.max(abs_amplitudes), 6),
                'mean_amplitude_abs': round(np.mean(abs_amplitudes), 6),
                'median_amplitude_abs': round(np.median(abs_amplitudes), 6),
                'std_amplitude_abs': round(np.std(abs_amplitudes), 8),
                'rms_amplitude': round(np.sqrt(np.mean(audio_data**2)), 6),
                
                # Процентили (игнорируют выбросы)
                'p01_amplitude': round(np.percentile(abs_amplitudes, 1), 8),
                'p05_amplitude': round(np.percentile(abs_amplitudes, 5), 8),
                'p10_amplitude': round(np.percentile(abs_amplitudes, 10), 8),
                'p25_amplitude': round(np.percentile(abs_amplitudes, 25), 8),
                'p50_amplitude': round(np.percentile(abs_amplitudes, 50), 8),
                'p75_amplitude': round(np.percentile(abs_amplitudes, 75), 8),
                'p90_amplitude': round(np.percentile(abs_amplitudes, 90), 8),
                'p95_amplitude': round(np.percentile(abs_amplitudes, 95), 8),
                'p99_amplitude': round(np.percentile(abs_amplitudes, 99), 8),
                
                # Практические метрики
                'dynamic_range_db': round(20 * np.log10(np.max(abs_amplitudes) / 
                                                       np.max([np.min(abs_amplitudes), 1e-10])), 2),
                'crest_factor': round(np.max(abs_amplitudes) / 
                                     np.max([np.sqrt(np.mean(audio_data**2)), 1e-10]), 2)
            }
            
            return stats
        except Exception as e:
            raise Exception(f"Ошибка при получении статистики сигнала {file_path}: {e}")