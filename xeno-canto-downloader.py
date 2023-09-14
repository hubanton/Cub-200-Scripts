from xenopy import Query

q = Query(name="Sooty Albatross")

q.retrieve_recordings(multiprocess=True, nproc=10, attempts=10, outdir="datasets/")

metafiles = q.retrieve_meta(verbose=True)