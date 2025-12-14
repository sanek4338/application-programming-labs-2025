"""Модуль для генерации графиков."""
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from typing import Optional


class PlotGenerator:
    """Класс для создания графиков из данных DataFrame."""
    
    @staticmethod
    def create_amplitude_plot(df: pd.DataFrame, output_path: str) -> None:
        if 'min_amplitude_abs' not in df.columns:
            raise ValueError("Отсутствует колонка 'min_amplitude_abs' в DataFrame")
        
        try:
            # Создаем директорию, если её нет
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Создаем фигуру и оси
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # Данные для графиков
            min_amplitudes = df['min_amplitude_abs']
            sorted_min_amplitudes = min_amplitudes.sort_values().reset_index(drop=True)
            
            # 1. Гистограмма минимальных амплитуд
            n_bins = min(30, max(10, int(len(min_amplitudes) / 5)))
            
            n, bins, patches = ax1.hist(min_amplitudes, bins=n_bins, 
                                       edgecolor='black', alpha=0.7, 
                                       color='skyblue', density=False)
            
            # Раскрашиваем столбцы гистограммы
            for i, patch in enumerate(patches):
                patch.set_facecolor(plt.cm.viridis(i / len(patches)))
            
            ax1.set_title('Гистограмма минимальных амплитуд (по модулю)', 
                         fontsize=12, fontweight='bold')
            ax1.set_xlabel('Минимальная амплитуда (по модулю)', fontsize=10)
            ax1.set_ylabel('Количество файлов', fontsize=10)
            ax1.grid(True, alpha=0.3, linestyle='--')
            
            # Статистика для гистограммы
            stats_text = f"""Статистика минимальных амплитуд:
Файлов: {len(min_amplitudes):,}
Min: {min_amplitudes.min():.6f}
Max: {min_amplitudes.max():.6f}
Mean: {min_amplitudes.mean():.6f}
Median: {min_amplitudes.median():.6f}
Std: {min_amplitudes.std():.6f}"""
            
            ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
                    verticalalignment='top', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
            
            # 2. Точечный график отсортированных минимальных амплитуд
            ax2.scatter(range(len(sorted_min_amplitudes)), sorted_min_amplitudes, 
                       alpha=0.6, s=20, color='coral', edgecolors='black', linewidth=0.3)
            
            # Линия тренда
            if len(sorted_min_amplitudes) > 1:
                z = np.polyfit(range(len(sorted_min_amplitudes)), sorted_min_amplitudes, 1)
                p = np.poly1d(z)
                ax2.plot(range(len(sorted_min_amplitudes)), p(range(len(sorted_min_amplitudes))), 
                        "r--", alpha=0.8, linewidth=1.5, label='Тренд')
            
            ax2.set_title('Отсортированные минимальные амплитуды', 
                         fontsize=12, fontweight='bold')
            ax2.set_xlabel('Порядковый номер файла', fontsize=10)
            ax2.set_ylabel('Минимальная амплитуда (по модулю)', fontsize=10)
            ax2.grid(True, alpha=0.3)
            ax2.legend(fontsize=9)
            
            # Горизонтальные линии для среднего и медианы
            ax2.axhline(y=min_amplitudes.mean(), color='green', linestyle=':', 
                       linewidth=1.5, alpha=0.7, label=f'Mean: {min_amplitudes.mean():.6f}')
            ax2.axhline(y=min_amplitudes.median(), color='blue', linestyle=':', 
                       linewidth=1.5, alpha=0.7, label=f'Median: {min_amplitudes.median():.6f}')
            
            ax2.legend(loc='lower right', fontsize=9)
            
            # 3. Box plot минимальных амплитуд
            bp = ax3.boxplot(min_amplitudes, vert=True, patch_artist=True)
            bp['boxes'][0].set_facecolor('lightblue')
            bp['medians'][0].set_color('red')
            bp['whiskers'][0].set_color('black')
            bp['whiskers'][1].set_color('black')
            
            ax3.set_title('Box plot минимальных амплитуд', 
                         fontsize=12, fontweight='bold')
            ax3.set_ylabel('Минимальная амплитуда (по модулю)', fontsize=10)
            ax3.grid(True, alpha=0.3, axis='y')
            
            # Добавляем значения квартилей
            q1 = np.percentile(min_amplitudes, 25)
            q3 = np.percentile(min_amplitudes, 75)
            iqr = q3 - q1
            
            box_stats = f"""Box Plot Statistics:
Q1 (25%): {q1:.6f}
Q2 (Median): {min_amplitudes.median():.6f}
Q3 (75%): {q3:.6f}
IQR: {iqr:.6f}
Outliers: {np.sum((min_amplitudes < (q1 - 1.5*iqr)) | 
                  (min_amplitudes > (q3 + 1.5*iqr)))}"""
            
            ax3.text(0.02, 0.98, box_stats, transform=ax3.transAxes,
                    verticalalignment='top', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))
            
            # 4. Cumulative distribution function (CDF)
            sorted_vals = np.sort(min_amplitudes)
            cdf = np.arange(1, len(sorted_vals) + 1) / len(sorted_vals)
            
            ax4.plot(sorted_vals, cdf, 'b-', linewidth=2)
            ax4.fill_between(sorted_vals, 0, cdf, alpha=0.3, color='blue')
            
            ax4.set_title('CDF минимальных амплитуд', 
                         fontsize=12, fontweight='bold')
            ax4.set_xlabel('Минимальная амплитуда (по модулю)', fontsize=10)
            ax4.set_ylabel('Вероятность', fontsize=10)
            ax4.grid(True, alpha=0.3)
            
            # Добавляем перцентили
            percentiles = [25, 50, 75, 90, 95]
            for p in percentiles:
                val = np.percentile(min_amplitudes, p)
                ax4.axvline(x=val, color='red', linestyle='--', alpha=0.5, linewidth=1)
                ax4.text(val, 0.5, f'{p}%', rotation=90, verticalalignment='center',
                        fontsize=8, color='red')
            
            cdf_stats = f"""CDF Statistics:
P25: {np.percentile(min_amplitudes, 25):.6f}
P50: {np.percentile(min_amplitudes, 50):.6f}
P75: {np.percentile(min_amplitudes, 75):.6f}
P90: {np.percentile(min_amplitudes, 90):.6f}
P95: {np.percentile(min_amplitudes, 95):.6f}"""
            
            ax4.text(0.02, 0.98, cdf_stats, transform=ax4.transAxes,
                    verticalalignment='top', fontsize=9,
                    bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.9))
            
            # Настраиваем общий вид
            plt.suptitle('Анализ минимальных амплитуд аудиофайлов (по модулю)', 
                        fontsize=16, fontweight='bold', y=1.02)
            plt.tight_layout()
            
            # Сохраняем график
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            raise Exception(f"Ошибка при создании графика: {e}")
    
    @staticmethod
    def create_comparison_plot(df: pd.DataFrame, output_path: str) -> None:
        try:
            # Проверяем наличие необходимых колонок
            required_cols = ['min_amplitude_abs', 'max_amplitude_abs', 'mean_amplitude_abs']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                print(f"Предупреждение: отсутствуют колонки {missing_cols}")
                return
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            axes = axes.flatten()
            
            # 1. Сравнение трех метрик амплитуд
            metrics = ['min_amplitude_abs', 'mean_amplitude_abs', 'max_amplitude_abs']
            labels = ['Минимальная', 'Средняя', 'Максимальная']
            colors = ['skyblue', 'lightgreen', 'salmon']
            
            for i, (metric, label, color) in enumerate(zip(metrics, labels, colors)):
                data = df[metric]
                axes[0].plot(range(len(data)), data.sort_values().values, 
                           label=f'{label} амплитуда', color=color, linewidth=2, alpha=0.7)
            
            axes[0].set_title('Сравнение амплитудных метрик (отсортировано)', 
                             fontsize=12, fontweight='bold')
            axes[0].set_xlabel('Порядковый номер файла', fontsize=10)
            axes[0].set_ylabel('Амплитуда (по модулю)', fontsize=10)
            axes[0].grid(True, alpha=0.3)
            axes[0].legend(fontsize=9)
            
            # 2. Соотношение Min/Max амплитуд
            if 'max_amplitude_abs' in df.columns and 'min_amplitude_abs' in df.columns:
                # Избегаем деления на ноль
                epsilon = 1e-10
                ratio = df['max_amplitude_abs'] / (df['min_amplitude_abs'] + epsilon)
                
                axes[1].hist(np.log10(ratio + 1e-10), bins=20, edgecolor='black', 
                           alpha=0.7, color='purple')
                axes[1].set_title('Распределение логарифма отношения Max/Min амплитуд', 
                                 fontsize=12, fontweight='bold')
                axes[1].set_xlabel('log10(Max / Min амплитуда)', fontsize=10)
                axes[1].set_ylabel('Количество файлов', fontsize=10)
                axes[1].grid(True, alpha=0.3)
            
            # 3. Scatter plot Min vs Mean амплитуд
            axes[2].scatter(df['min_amplitude_abs'], df['mean_amplitude_abs'], 
                          alpha=0.5, s=20, color='teal', edgecolors='black', linewidth=0.3)
            
            # Линия y=x для сравнения
            max_val = max(df['min_amplitude_abs'].max(), df['mean_amplitude_abs'].max())
            axes[2].plot([0, max_val], [0, max_val], 'r--', alpha=0.7, 
                       label='y = x (Min = Mean)')
            
            axes[2].set_title('Минимальная vs Средняя амплитуда', 
                             fontsize=12, fontweight='bold')
            axes[2].set_xlabel('Минимальная амплитуда', fontsize=10)
            axes[2].set_ylabel('Средняя амплитуда', fontsize=10)
            axes[2].grid(True, alpha=0.3)
            axes[2].legend(fontsize=9)
            
            # 4. Scatter plot Mean vs Max амплитуд
            axes[3].scatter(df['mean_amplitude_abs'], df['max_amplitude_abs'], 
                          alpha=0.5, s=20, color='orange', edgecolors='black', linewidth=0.3)
            
            # Линия y=x для сравнения
            max_val2 = max(df['mean_amplitude_abs'].max(), df['max_amplitude_abs'].max())
            axes[3].plot([0, max_val2], [0, max_val2], 'r--', alpha=0.7, 
                       label='y = x (Mean = Max)')
            
            axes[3].set_title('Средняя vs Максимальная амплитуда', 
                             fontsize=12, fontweight='bold')
            axes[3].set_xlabel('Средняя амплитуда', fontsize=10)
            axes[3].set_ylabel('Максимальная амплитуда', fontsize=10)
            axes[3].grid(True, alpha=0.3)
            axes[3].legend(fontsize=9)
            
            plt.suptitle('Сравнительный анализ амплитудных характеристик аудиофайлов', 
                        fontsize=16, fontweight='bold', y=1.02)
            plt.tight_layout()
            
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            raise Exception(f"Ошибка при создании сравнительного графика: {e}")