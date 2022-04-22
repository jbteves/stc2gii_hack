import mne
import nibabel as nib
import numpy as np

def get_decimated_surfaces(src):
    """Get the decimated surfaces from a source space.
    Parameters
    ----------
    src : instance of SourceSpaces | path-like
        The source space with decimated surfaces.
    Returns
    -------
    surfaces : list of dict
        The decimated surfaces present in the source space. Each dict
        which contains 'rr' and 'tris' keys for vertices positions and
        triangle indices.
    Notes
    -----
    .. versionadded:: 1.0
    """
    src = mne.read_source_spaces(src)
    surfaces = []
    for s in src:
        if s['type'] != 'surf':
            continue
        rr = s['rr']
        use_tris = s['use_tris']
        vertno = s['vertno']
        ss = {}
        ss['rr'] = rr[vertno]
        reindex = np.full(len(rr), -1, int)
        reindex[vertno] = np.arange(len(vertno))
        ss['tris'] = reindex[use_tris]
        assert (ss['tris'] >= 0).all()
        surfaces.append(ss)
    return surfaces


def to_gii_simple(fif, stc, basename, scale=1e3, scale_rr=1e3):
    """Convert a FIF and STC file into GIFTI format

    Parameters
    ----------
    fif: str
        The source spaces file
    stc: str or list(str)
        The source reconstruction STC file(s)
    basename: str
        The basename to use for the giftis
    scale: float
        The amount to scale the STC data by, default 1e3

    Notes
    -----
    Creates gifti files based on the basename
    """
    fif_ob = get_decimated_surfaces(fif)
    stc_ob = [mne.read_source_estimate(f) for f in stc]
    if len(fif_ob) != 2:
        raise ValueError(f"fif object contains {len(fif_ob)} items, should be exactly 2")
    if len(stc_ob) != 2:
        raise ValueError(f"stc object contains {len(stc_ob)} items, should be exactly 2")
    # Create lists to put DataArrays into
    lh = []
    rh = []
    ss = fif_ob
    stc = stc_ob
    # Coerce rr to be in mm (MNE uses meters)
    ss[0]['rr'] *= scale_rr
    ss[1]['rr'] *= scale_rr
    # Make the coordinate DataArrays and append them
    lh.append(nib.gifti.gifti.GiftiDataArray(data=ss[0]['rr'], intent='NIFTI_INTENT_POINTSET', datatype='NIFTI_TYPE_FLOAT32'))
    rh.append(nib.gifti.gifti.GiftiDataArray(data=ss[1]['rr'], intent='NIFTI_INTENT_POINTSET', datatype='NIFTI_TYPE_FLOAT32'))
    # Make the topology DataArray
    lh.append(nib.gifti.gifti.GiftiDataArray(data=ss[0]['tris'], intent='NIFTI_INTENT_TRIANGLE', datatype='NIFTI_TYPE_INT32'))
    rh.append(nib.gifti.gifti.GiftiDataArray(data=ss[1]['tris'], intent='NIFTI_INTENT_TRIANGLE', datatype='NIFTI_TYPE_INT32'))
    # Make the output GIFTI
    topo_gi_lh = nib.gifti.gifti.GiftiImage(darrays=lh)
    topo_gi_rh = nib.gifti.gifti.GiftiImage(darrays=rh)
    nib.save(topo_gi_lh, f"{basename}-lh.gii")
    nib.save(topo_gi_rh, f"{basename}-rh.gii")
    # Make the Time Series data arrays
    lh_ts = []
    rh_ts = []
    for t in range(stc[0].shape[1]):
        lh_ts.append(
            nib.gifti.gifti.GiftiDataArray(
                data=stc[0].lh_data[:, t] * scale,
                intent='NIFTI_INTENT_POINTSET',
                datatype='NIFTI_TYPE_FLOAT32'
            )
        )
        rh_ts.append(
            nib.gifti.gifti.GiftiDataArray(
                data=stc[1].rh_data[:, t] * scale,
                intent='NIFTI_INTENT_POINTSET',
                datatype='NIFTI_TYPE_FLOAT32'
            )
        )
    # Save the time series
    ts_gi_lh = nib.gifti.gifti.GiftiImage(darrays=lh_ts)
    ts_gi_rh = nib.gifti.gifti.GiftiImage(darrays=rh_ts)
    nib.save(ts_gi_lh, f"{basename}-lh.time.gii")
    nib.save(ts_gi_rh, f"{basename}-rh.time.gii")
