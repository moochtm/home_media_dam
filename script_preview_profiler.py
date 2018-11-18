import cProfile

from src.api.core import utils_preview

file_path = '/Users/home/Pictures/ORIGINALS/buffer/345/test3.jpg'

method_to_profile = 'utils_preview.get_binary_and_mime(full_path=file_path, longest_edge_res=1920)'

cProfile.run(method_to_profile)