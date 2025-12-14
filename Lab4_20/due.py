"""Модуль для работы с DataFrame и анализа данных."""
import os
from typing import Any, Dict
import pandas as pd
from hoi import AudioProcessor


class DataFrameManager:
    """Класс для управления DataFrame с аудиофайлами."""

    def __init__(self):
        """Инициализирует менеджер DataFrame."""
        self.df = pd.DataFrame()
        self.audio_processor = AudioProcessor()

    def create_dataframe_from_annotation(self, csv_path: str) -> pd.DataFrame:
        """
        Создает DataFrame из CSV аннотации.
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Файл аннотации не найден: {csv_path}")

        try:
            self.df = pd.read_csv(csv_path)

            # Проверяем наличие нужных колонок
            if 'absolute_path' in self.df.columns:
                self.df = self.df.rename(columns={'absolute_path': 'absolute_file_path'})
            if 'relative_path' in self.df.columns:
                self.df = self.df.rename(columns={'relative_path': 'relative_file_path'})
            if 'filename' in self.df.columns:
                self.df = self.df.rename(columns={'filename': 'audio_name'})

            # Проверяем, что абсолютные пути существуют
            if 'absolute_file_path' not in self.df.columns and len(self.df.columns) > 0:
                # Пробуем использовать первую колонку как путь
                first_col = self.df.columns[0]
                self.df['absolute_file_path'] = self.df[first_col]
                
            if 'relative_file_path' not in self.df.columns:
                self.df['relative_file_path'] = self.df['absolute_file_path'].apply(
                    lambda x: os.path.basename(str(x)) if pd.notna(x) else ''
                )

            print(f"Загружено {len(self.df)} записей из аннотации")
            
            # Проверяем существование файлов
            existing_files = []
            missing_files = []
            
            for idx, row in self.df.iterrows():
                file_path = str(row['absolute_file_path'])
                if os.path.exists(file_path):
                    existing_files.append(idx)
                else:
                    missing_files.append((idx, file_path))
            
            if missing_files:
                print(f"Предупреждение: {len(missing_files)} файлов не найдено")
                for idx, file_path in missing_files[:5]:  # Показываем первые 5
                    print(f"  Строка {idx}: {file_path}")
                if len(missing_files) > 5:
                    print(f"  ... и еще {len(missing_files) - 5} файлов")

            return self.df

        except Exception as e:
            raise Exception(f"Ошибка при создании DataFrame: {e}")

    def add_amplitude_columns(self, use_practical: bool = False) -> None:
        """
        Добавляет колонки с амплитудными характеристиками.
        
        Args:
            use_practical: Использовать практические метрики (игнорирующие шум)
        """
        if 'absolute_file_path' not in self.df.columns:
            raise ValueError("Отсутствует колонка с абсолютными путями")

        try:
            print("Добавление амплитудных характеристик...")
            
            # Собираем статистику для каждого файла
            amplitude_data = []
            
            for idx, row in self.df.iterrows():
                file_path = str(row['absolute_file_path'])
                
                if pd.notna(file_path) and os.path.exists(file_path):
                    try:
                        stats = self.audio_processor.get_amplitude_statistics(file_path)
                        amplitude_data.append(stats)
                    except Exception as e:
                        print(f"Ошибка обработки файла {file_path}: {e}")
                        amplitude_data.append({})
                else:
                    amplitude_data.append({})
            
            # Создаем DataFrame из собранной статистики
            stats_df = pd.DataFrame(amplitude_data)
            
            # Добавляем колонки в основной DataFrame
            for col in stats_df.columns:
                self.df[col] = stats_df[col]
            
            print(f"Добавлено {len(stats_df.columns)} амплитудных характеристик")
            
            # Для обратной совместимости оставляем основную колонку
            if 'min_amplitude_abs' in self.df.columns:
                self.df['min_amplitude'] = self.df['min_amplitude_abs']
            
        except Exception as e:
            raise Exception(f"Ошибка при добавлении амплитудных колонок: {e}")

    def sort_by_amplitude(self, column: str = 'p05_amplitude', ascending: bool = True) -> pd.DataFrame:
        try:
            if column not in self.df.columns:
                # Если колонки нет, используем 5-й процентиль по умолчанию
                column = 'p05_amplitude' if 'p05_amplitude' in self.df.columns else 'min_amplitude_abs'
            
            sorted_df = self.df.sort_values(column, ascending=ascending, na_position='last')
            print(f"Отсортировано по колонке '{column}' ({'по возрастанию' if ascending else 'по убыванию'})")
            return sorted_df

        except Exception as e:
            raise Exception(f"Ошибка при сортировке: {e}")

    def filter_by_amplitude(self, 
                           column: str = 'p05_amplitude',
                           min_value: float = 0, 
                           max_value: float = None) -> pd.DataFrame:
        try:
            if column not in self.df.columns:
                # Если колонки нет, используем 5-й процентиль по умолчанию
                column = 'p05_amplitude' if 'p05_amplitude' in self.df.columns else 'min_amplitude_abs'
            
            filtered_df = self.df.copy()
            
            if min_value is not None:
                before = len(filtered_df)
                filtered_df = filtered_df[filtered_df[column] >= min_value]
                after = len(filtered_df)
                print(f"Фильтр {column} >= {min_value}: {before} -> {after} файлов")
            
            if max_value is not None:
                before = len(filtered_df)
                filtered_df = filtered_df[filtered_df[column] <= max_value]
                after = len(filtered_df)
                print(f"Фильтр {column} <= {max_value}: {before} -> {after} файлов")
            
            return filtered_df

        except Exception as e:
            raise Exception(f"Ошибка при фильтрации: {e}")

    def save_dataframe(self, output_path: str) -> None:
        """Сохраняет DataFrame в CSV файл."""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Сохраняем все колонки
            self.df.to_csv(
                output_path, 
                index=False, 
                encoding='utf-8-sig',
                sep=','
            )
            print(f"DataFrame сохранен ({len(self.df)} записей, {len(self.df.columns)} колонок)")

        except Exception as e:
            raise Exception(f"Ошибка при сохранении DataFrame: {e}")

    def get_dataframe_info(self) -> Dict[str, Any]:
        """Возвращает информацию о DataFrame."""
        info = {
            'total_files': len(self.df),
            'columns': list(self.df.columns)
        }

        # Статистика по различным амплитудным метрикам
        amplitude_columns = [col for col in self.df.columns if 'amplitude' in col]
        
        for col in amplitude_columns:
            if col in self.df.columns and pd.api.types.is_numeric_dtype(self.df[col]):
                col_data = self.df[col].dropna()
                if len(col_data) > 0:
                    info[f'{col}_min'] = round(col_data.min(), 8)
                    info[f'{col}_max'] = round(col_data.max(), 6)
                    info[f'{col}_mean'] = round(col_data.mean(), 6)
                    info[f'{col}_median'] = round(col_data.median(), 6)
        
        return info