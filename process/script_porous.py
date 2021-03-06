import numpy as np
from skimage import data, measure, morphology
from scipy import ndimage

im = data.binary_blobs(length=400, n_dim=3, volume_fraction=0.33, seed=0)
mask = np.zeros(im.shape, dtype=np.bool)
mask[200:, 200:, 200:] = True
labels = ndimage.label(im)[0].astype(np.uint8)
sizes = np.bincount(labels.ravel())
order = np.argsort(sizes)
biggest_label = order[-2]
sorted_sizes = np.sort(sizes)[::-1]
ratio = sorted_sizes[1] / float(sorted_sizes[1:].sum())
print("ratio: ", ratio)
print("nb of labels: ", labels.max())

connected_phase = labels == biggest_label
skel = morphology.skeletonize_3d(connected_phase)
skel[mask] = 0
skel = morphology.binary_dilation(skel, selem=np.ones((3, 3, 3)))
distance = ndimage.distance_transform_cdt(connected_phase).astype(np.float32)
distance[skel == 0] = 0

from mayavi import mlab
fig = mlab.figure(bgcolor=(0, 0, 0))
labels[labels == biggest_label] = 0
sizes[:2] = 0
radii = sizes**0.33
labels = radii[labels]
labels[~mask] = 0
im = (labels > 0).astype(np.uint8)

src = mlab.pipeline.scalar_field(im)
src.image_data.point_data.add_array(labels.T.ravel())
# We need to give a name to our new dataset.
src.image_data.point_data.get_array(1).name = 'label'
src.update()
src2 = mlab.pipeline.set_active_attribute(src,
                                            point_scalars='scalar')
contour = mlab.pipeline.contour(src2)
contour2 = mlab.pipeline.set_active_attribute(contour,
                                            point_scalars='label')
mlab.pipeline.surface(contour2, colormap='cool')

skel_src = mlab.pipeline.scalar_field(skel.astype(np.uint8))
skel_src.image_data.point_data.add_array(distance.T.ravel())
# We need to give a name to our new dataset.
skel_src.image_data.point_data.get_array(1).name = 'distance'
skel_src.update()
skel_src2 = mlab.pipeline.set_active_attribute(skel_src,
                                            point_scalars='scalar')
skel_contour = mlab.pipeline.contour(skel_src2)
skel_contour2 = mlab.pipeline.set_active_attribute(skel_contour,
                                            point_scalars='distance')
mlab.pipeline.surface(skel_contour2, colormap='hot')


mlab.contour3d(connected_phase.astype(np.uint8), contours=[0.5], opacity=0.1, colormap='cool')
mlab.outline()
