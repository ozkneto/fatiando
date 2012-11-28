"""
Seis: 2D straight-ray tomography using sharpness (total variation)
regularization

Uses synthetic data and a model generated from an image file.
"""
import urllib
import time
from os import path
import numpy
import fatiando as ft

log = ft.logger.get()
log.info(ft.logger.header())
log.info(__doc__)

area = (0, 100000, 0, 100000)
shape = (30, 30)
model = ft.mesher.SquareMesh(area, shape)
# Fetch the image from the online docs
urllib.urlretrieve(
    'http://fatiando.readthedocs.org/en/latest/_static/logo.png', 'logo.png')
vmin, vmax = 4000, 10000
model.img2prop('logo.png', vmin, vmax, 'vp')

# Make some travel time data and add noise
log.info("Generating synthetic travel-time data")
src_loc = ft.utils.random_points(area, 80)
rec_loc = ft.utils.circular_points(area, 30, random=True)
srcs, recs = ft.utils.connect_points(src_loc, rec_loc)
start = time.time()
tts = ft.seis.ttime2d.straight(model, 'vp', srcs, recs, par=True)
log.info("  time: %s" % (ft.utils.sec2hms(time.time() - start)))
tts, error = ft.utils.contaminate(tts, 0.01, percent=True, return_stddev=True)
# Make the mesh
mesh = ft.mesher.SquareMesh(area, shape)
# and run the inversion
estimate, residuals = ft.seis.srtomo.run(tts, srcs, recs, mesh, sharp=5*10**5)
# Convert the slowness estimate to velocities and add it the mesh
mesh.addprop('vp', ft.seis.srtomo.slowness2vel(estimate))

# Calculate and print the standard deviation of the residuals
# it should be close to the data error if the inversion was able to fit the data
log.info("Assumed error: %f" % (error))
log.info("Standard deviation of residuals: %f" % (numpy.std(residuals)))

ft.vis.figure(figsize=(14, 5))
ft.vis.subplot(1, 2, 1)
ft.vis.axis('scaled')
ft.vis.title('Vp synthetic model of the Earth')
ft.vis.squaremesh(model, prop='vp', vmin=vmin, vmax=vmax,
    cmap=ft.vis.cm.seismic)
cb = ft.vis.colorbar()
cb.set_label('Velocity')
ft.vis.points(src_loc, '*y', label="Sources")
ft.vis.points(rec_loc, '^r', label="Receivers")
ft.vis.legend(loc='lower left', shadow=True, numpoints=1, prop={'size':10})
ft.vis.m2km()
ft.vis.subplot(1, 2, 2)
ft.vis.axis('scaled')
ft.vis.title('Tomography result (sharp)')
ft.vis.squaremesh(mesh, prop='vp', vmin=vmin, vmax=vmax,
    cmap=ft.vis.cm.seismic)
cb = ft.vis.colorbar()
cb.set_label('Velocity')
ft.vis.m2km()
ft.vis.figure()
ft.vis.grid()
ft.vis.title('Residuals (data with %.4f s error)' % (error))
ft.vis.hist(residuals, color='gray', bins=10)
ft.vis.xlabel("seconds")
ft.vis.show()
