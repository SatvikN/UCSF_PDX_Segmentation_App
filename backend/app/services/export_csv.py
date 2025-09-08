from typing import Iterable, List
import csv


def write_volumes_csv(images_dcm: List[str], scaled_slice_areas: Iterable[float], total_volume: float, csv_filename: str) -> None:
    scaled_slice_areas_list = list(scaled_slice_areas)
    if len(images_dcm) != len(scaled_slice_areas_list):
        raise ValueError("images_dcm and scaled_slice_areas length mismatch")

    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Slice', 'Area (cc)'])
        for i in range(len(images_dcm)):
            writer.writerow([images_dcm[i], scaled_slice_areas_list[i]])
        writer.writerow(["Total tumor volume (cc)", total_volume])


