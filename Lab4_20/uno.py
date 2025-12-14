"""Основной модуль для третьей лабораторной работы."""
import argparse
import os
from due import DataFrameManager
from toy import PlotGenerator
import pandas as pd


def parse_args() -> argparse.Namespace:
    """
    Парсит аргументы командной строки.
    """
    parser = argparse.ArgumentParser(
        description="Анализ амплитудных характеристик аудиофайлов"
    )
    parser.add_argument(
        "--annotation",
        required=True,
        help="Путь к CSV файлу аннотации"
    )
    parser.add_argument(
        "--output_df",
        default="results/audio_analysis.csv",
        help="Путь для сохранения DataFrame"
    )
    parser.add_argument(
        "--output_plot",
        default="results/amplitude_analysis.png", 
        help="Путь для сохранения графика"
    )
    parser.add_argument(
        "--filter_column",
        default="p05_amplitude",
        help="Колонка для фильтрации (min_amplitude_abs, p01_amplitude, p05_amplitude и т.д.)"
    )
    parser.add_argument(
        "--min_value",
        type=float,
        default=0.000001,  # Более реалистичное значение по умолчанию
        help="Минимальное значение амплитуды для фильтрации"
    )
    parser.add_argument(
        "--max_value",
        type=float,
        default=0.1,
        help="Максимальное значение амплитуды для фильтрации"
    )
    parser.add_argument(
        "--sort_column",
        default="p05_amplitude",
        help="Колонка для сортировки"
    )
    parser.add_argument(
        "--sort_ascending",
        action="store_true",
        help="Сортировать по возрастанию (по умолчанию - по убыванию)"
    )
    return parser.parse_args()


def print_amplitude_info(df: pd.DataFrame) -> None:
    """Выводит информацию об амплитудах."""
    print("\n" + "="*70)
    print("СТАТИСТИКА АМПЛИТУДНЫХ ХАРАКТЕРИСТИК")
    print("="*70)
    
    amplitude_columns = [col for col in df.columns if 'amplitude' in col]
    
    for col in amplitude_columns[:10]:  # Показываем первые 10 метрик
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            data = df[col].dropna()
            if len(data) > 0:
                print(f"\n{col}:")
                print(f"  Min: {data.min():.8f}")
                print(f"  Max: {data.max():.6f}")
                print(f"  Mean: {data.mean():.6f}")
                print(f"  Median: {data.median():.6f}")
                print(f"  Std: {data.std():.8f}")
    
    if len(amplitude_columns) > 10:
        print(f"\n... и еще {len(amplitude_columns) - 10} амплитудных метрик")
    
    print("="*70)


def main() -> None:
    """Основная функция программы."""
    try:
        args = parse_args()

        df_manager = DataFrameManager()

        print("\n" + "="*70)
        print("АНАЛИЗ АМПЛИТУДНЫХ ХАРАКТЕРИСТИК АУДИОФАЙЛОВ")
        print("="*70)

        print("\n1. Создание DataFrame из аннотации...")
        df = df_manager.create_dataframe_from_annotation(args.annotation)
        print(f"DataFrame создан. Колонки: {list(df.columns)}")

        print("\n2. Добавление амплитудных характеристик...")
        df_manager.add_amplitude_columns()
        print("Амплитудные характеристики добавлены")

        # Выводим информацию об амплитудах
        print_amplitude_info(df_manager.df)

        print(f"\n3. Фильтрация по колонке '{args.filter_column}'...")
        print(f"   Диапазон: [{args.min_value}, {args.max_value}]")
        
        filtered_df = df_manager.filter_by_amplitude(
            column=args.filter_column,
            min_value=args.min_value,
            max_value=args.max_value
        )
        
        print(f"   Результат: {len(filtered_df)} файлов соответствуют критериям")

        print(f"\n4. Сортировка по колонке '{args.sort_column}'...")
        sort_order = "возрастанию" if args.sort_ascending else "убыванию"
        print(f"   Порядок: по {sort_order}")
        
        sorted_df = df_manager.sort_by_amplitude(
            column=args.sort_column,
            ascending=args.sort_ascending
        )

        print("\n5. Создание графиков...")
        plot_generator = PlotGenerator()
        
        # Основной график
        plot_generator.create_amplitude_plot(sorted_df, args.output_plot)
        print(f"   График сохранен: {args.output_plot}")

        print("\n6. Сохранение результатов...")
        df_manager.save_dataframe(args.output_df)
        print(f"   DataFrame сохранен: {args.output_df}")

        print("\n" + "="*70)
        print("РЕКОМЕНДАЦИИ ПО ИСПОЛЬЗОВАНИЮ:")
        print("="*70)
        print("Для получения осмысленных результатов используйте:")
        print("1. p01_amplitude или p05_amplitude (игнорируют выбросы)")
        print("2. Более реалистичные диапазоны значений:")
        print("   --min_value 0.00001 --max_value 0.1")
        print("3. Проверьте существование файлов по указанным путям")
        print("="*70)

    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()