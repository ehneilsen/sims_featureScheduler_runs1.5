import numpy as np
import matplotlib.pylab as plt
import healpy as hp
from lsst.sims.featureScheduler.modelObservatory import Model_observatory
from lsst.sims.featureScheduler.schedulers import Core_scheduler, simple_filter_sched
from lsst.sims.featureScheduler.utils import standard_goals, create_season_offset, empty_observation
import lsst.sims.featureScheduler.basis_functions as bf
from lsst.sims.featureScheduler.surveys import (Greedy_survey,
                                                Blob_survey)
from lsst.sims.featureScheduler import sim_runner
import lsst.sims.featureScheduler.detailers as detailers
import sys
import subprocess
import os
import argparse
from lsst.sims.featureScheduler.surveys import Deep_drilling_survey
import lsst.sims.featureScheduler.basis_functions as basis_functions


def dd_bfs(RA, dec, survey_name, ha_limits, frac_total=0.007, aggressive_frac=0.005):
    """
    Convienence function to generate all the feasibility basis functions
    """
    sun_alt_limit = -18.
    time_needed = 9.
    fractions = [0.00, aggressive_frac, frac_total]
    bfs = []
    bfs.append(basis_functions.Filter_loaded_basis_function(filternames=['r', 'g', 'i', 'z', 'y']))
    bfs.append(basis_functions.Not_twilight_basis_function(sun_alt_limit=sun_alt_limit))
    bfs.append(basis_functions.Time_to_twilight_basis_function(time_needed=time_needed))
    bfs.append(basis_functions.Hour_Angle_limit_basis_function(RA=RA, ha_limits=ha_limits))
    bfs.append(basis_functions.Fraction_of_obs_basis_function(frac_total=frac_total, survey_name=survey_name))
    bfs.append(basis_functions.Look_ahead_ddf_basis_function(frac_total, aggressive_frac,
                                                             sun_alt_limit=sun_alt_limit, time_needed=time_needed,
                                                             RA=RA, survey_name=survey_name,
                                                             ha_limits=ha_limits))
    bfs.append(basis_functions.Soft_delay_basis_function(fractions=fractions, delays=[0., 0.04, 1.5],
                                                         survey_name=survey_name))

    return bfs


def dd_u_bfs(RA, dec, survey_name, ha_limits, frac_total=0.0019, aggressive_frac=0.0014):
    """Convienence function to generate all the feasibility basis functions for u-band DDFs
    """
    bfs = []
    sun_alt_limit = -18.
    time_needed = 6.
    fractions = [0.00, aggressive_frac, frac_total]
    bfs.append(basis_functions.Filter_loaded_basis_function(filternames='u'))
    bfs.append(basis_functions.Not_twilight_basis_function(sun_alt_limit=sun_alt_limit))
    bfs.append(basis_functions.Time_to_twilight_basis_function(time_needed=time_needed))
    bfs.append(basis_functions.Hour_Angle_limit_basis_function(RA=RA, ha_limits=ha_limits))
    bfs.append(basis_functions.Moon_down_basis_function())
    bfs.append(basis_functions.Fraction_of_obs_basis_function(frac_total=frac_total, survey_name=survey_name))
    bfs.append(basis_functions.Look_ahead_ddf_basis_function(frac_total, aggressive_frac,
                                                             sun_alt_limit=sun_alt_limit, time_needed=time_needed,
                                                             RA=RA, survey_name=survey_name,
                                                             ha_limits=ha_limits))
    bfs.append(basis_functions.Soft_delay_basis_function(fractions=fractions, delays=[0., 0.2, 0.5],
                                                         survey_name=survey_name))

    return bfs


def generate_dd_surveys(nside=None, nexp=2, detailers=None):
    """Utility to return a list of standard deep drilling field surveys.

    XXX-Someone double check that I got the coordinates right!

    """

    surveys = []

    # ELAIS S1
    RA = 9.45
    dec = -44.
    survey_name = 'DD:ELAISS1'
    ha_limits = ([0., 1.5], [21.5, 24.])
    bfs = dd_bfs(RA, dec, survey_name, ha_limits)
    surveys.append(Deep_drilling_survey(bfs, RA, dec, sequence='grizy',
                                        nvis=[1, 1, 3, 5, 4],
                                        survey_name=survey_name, reward_value=100,
                                        nside=nside, nexp=nexp, detailers=detailers))

    survey_name = 'DD:u,ELAISS1'
    bfs = dd_u_bfs(RA, dec, survey_name, ha_limits)

    surveys.append(Deep_drilling_survey(bfs, RA, dec, sequence='u',
                                        nvis=[8], survey_name=survey_name, reward_value=100, nside=nside,
                                        nexp=nexp, detailers=detailers))

    # XMM-LSS
    survey_name = 'DD:XMM-LSS'
    RA = 35.708333
    dec = -4-45/60.
    ha_limits = ([0., 1.5], [21.5, 24.])
    bfs = dd_bfs(RA, dec, survey_name, ha_limits)

    surveys.append(Deep_drilling_survey(bfs, RA, dec, sequence='grizy',
                                        nvis=[1, 1, 3, 5, 4], survey_name=survey_name, reward_value=100,
                                        nside=nside, nexp=nexp, detailers=detailers))
    survey_name = 'DD:u,XMM-LSS'
    bfs = dd_u_bfs(RA, dec, survey_name, ha_limits)

    surveys.append(Deep_drilling_survey(bfs, RA, dec, sequence='u',
                                        nvis=[8], survey_name=survey_name, reward_value=100, nside=nside,
                                        nexp=nexp, detailers=detailers))

    # Extended Chandra Deep Field South
    RA = 53.125
    dec = -28.-6/60.
    survey_name = 'DD:ECDFS'
    ha_limits = [[0.5, 3.0], [20., 22.5]]
    bfs = dd_bfs(RA, dec, survey_name, ha_limits)
    surveys.append(Deep_drilling_survey(bfs, RA, dec, sequence='grizy',
                                        nvis=[1, 1, 3, 5, 4],
                                        survey_name=survey_name, reward_value=100, nside=nside,
                                        nexp=nexp, detailers=detailers))

    survey_name = 'DD:u,ECDFS'
    bfs = dd_u_bfs(RA, dec, survey_name, ha_limits)
    surveys.append(Deep_drilling_survey(bfs, RA, dec, sequence='u',
                                        nvis=[8], survey_name=survey_name, reward_value=100, nside=nside,
                                        nexp=nexp, detailers=detailers))
    # COSMOS
    RA = 150.1
    dec = 2.+10./60.+55/3600.
    survey_name = 'DD:COSMOS'
    ha_limits = ([0., 2.5], [21.5, 24.])
    bfs = dd_bfs(RA, dec, survey_name, ha_limits)
    surveys.append(Deep_drilling_survey(bfs, RA, dec, sequence='grizy',
                                        nvis=[1, 1, 3, 5, 4],
                                        survey_name=survey_name, reward_value=100, nside=nside,
                                        nexp=nexp, detailers=detailers))
    survey_name = 'DD:u,COSMOS'
    bfs = dd_u_bfs(RA, dec, survey_name, ha_limits)
    surveys.append(Deep_drilling_survey(bfs, RA, dec, sequence='u',
                                        nvis=[8], survey_name=survey_name, reward_value=100, nside=nside,
                                        nexp=nexp, detailers=detailers))

    # Euclid Fields
    # I can use the sequence kwarg to do two positions per sequence
    filters = 'grizy'
    nviss = [1, 1, 3, 5, 4]
    survey_name = 'DD:EDFS'
    # Note the sequences need to be in radians since they are using observation objects directly
    RAs = np.radians([58.97, 63.6])
    decs = np.radians([-49.28, -47.60])
    sequence = []
    exptime = 30
    for filtername, nvis in zip(filters, nviss):
        for ra, dec in zip(RAs, decs):
            for num in range(nvis):
                obs = empty_observation()
                obs['filter'] = filtername
                obs['exptime'] = exptime
                obs['RA'] = ra
                obs['dec'] = dec
                obs['nexp'] = nexp
                obs['note'] = survey_name
                sequence.append(obs)

    ha_limits = ([0., 1.5], [22.5, 24.])
    # And back to degrees for the basis function
    bfs = dd_bfs(np.degrees(RAs[0]), np.degrees(decs[0]), survey_name, ha_limits)
    surveys.append(Deep_drilling_survey(bfs, RA, dec, sequence=sequence,
                                        survey_name=survey_name, reward_value=100, nside=nside,
                                        nexp=nexp, detailers=detailers))

    filters = 'u'
    nviss = [4]
    survey_name = 'DD:u, EDFS'
    sequence = []
    exptime = 30
    for filtername, nvis in zip(filters, nviss):
        for ra, dec in zip(RAs, decs):
            for num in range(nvis):
                obs = empty_observation()
                obs['filter'] = filtername
                obs['exptime'] = exptime
                obs['RA'] = ra
                obs['dec'] = dec
                obs['nexp'] = nexp
                obs['note'] = survey_name
                sequence.append(obs)

    bfs = dd_u_bfs(np.degrees(RAs[0]), np.degrees(decs[0]), survey_name, ha_limits)
    surveys.append(Deep_drilling_survey(bfs, RA, dec, sequence=sequence,
                                        survey_name=survey_name, reward_value=100, nside=nside,
                                        nexp=nexp, detailers=detailers))

    return surveys


def gen_greedy_surveys(nside=32, nexp=1, exptime=30., filters=['r', 'i', 'z', 'y'],
                       camera_rot_limits=[-80., 80.],
                       shadow_minutes=60., max_alt=76., moon_distance=30., ignore_obs='DD',
                       m5_weight=3., footprint_weight=0.3, slewtime_weight=3.,
                       stayfilter_weight=3.):
    """
    Make a quick set of greedy surveys

    This is a convienence function to generate a list of survey objects that can be used with
    lsst.sims.featureScheduler.schedulers.Core_scheduler.
    To ensure we are robust against changes in the sims_featureScheduler codebase, all kwargs are
    explicitly set.

    Parameters
    ----------
    nside : int (32)
        The HEALpix nside to use
    nexp : int (1)
        The number of exposures to use in a visit.
    exptime : float (30.)
        The exposure time to use per visit (seconds)
    filters : list of str (['r', 'i', 'z', 'y'])
        Which filters to generate surveys for.
    camera_rot_limits : list of float ([-80., 80.])
        The limits to impose when rotationally dithering the camera (degrees).
    shadow_minutes : float (60.)
        Used to mask regions around zenith (minutes)
    max_alt : float (76.
        The maximium altitude to use when masking zenith (degrees)
    moon_distance : float (30.)
        The mask radius to apply around the moon (degrees)
    ignore_obs : str or list of str ('DD')
        Ignore observations by surveys that include the given substring(s).
    m5_weight : float (3.)
        The weight for the 5-sigma depth difference basis function
    footprint_weight : float (0.3)
        The weight on the survey footprint basis function.
    slewtime_weight : float (3.)
        The weight on the slewtime basis function
    stayfilter_weight : float (3.)
        The weight on basis function that tries to stay avoid filter changes.
    """
    # Define the extra parameters that are used in the greedy survey. I
    # think these are fairly set, so no need to promote to utility func kwargs
    greed_survey_params = {'block_size': 1, 'smoothing_kernel': None,
                           'seed': 42, 'camera': 'LSST', 'dither': True,
                           'survey_name': 'greedy'}

    footprints = standard_goals(nside=nside)
    sum_footprints = 0
    for key in footprints:
        sum_footprints += np.sum(footprints[key])

    surveys = []
    detailer = detailers.Camera_rot_detailer(min_rot=np.min(camera_rot_limits), max_rot=np.max(camera_rot_limits))

    for filtername in filters:
        bfs = []
        bfs.append((bf.M5_diff_basis_function(filtername=filtername, nside=nside), m5_weight))
        bfs.append((bf.Footprint_basis_function(filtername=filtername,
                                                footprint=footprints[filtername],
                                                out_of_bounds_val=np.nan, nside=nside,
                                                all_footprints_sum=sum_footprints), footprint_weight))
        bfs.append((bf.Slewtime_basis_function(filtername=filtername, nside=nside), slewtime_weight))
        bfs.append((bf.Strict_filter_basis_function(filtername=filtername), stayfilter_weight))
        # Masks, give these 0 weight
        bfs.append((bf.Zenith_shadow_mask_basis_function(nside=nside, shadow_minutes=shadow_minutes,
                                                         max_alt=max_alt), 0))
        bfs.append((bf.Moon_avoidance_basis_function(nside=nside, moon_distance=moon_distance), 0))

        bfs.append((bf.Filter_loaded_basis_function(filternames=filtername), 0))
        bfs.append((bf.Planet_mask_basis_function(nside=nside), 0))

        weights = [val[1] for val in bfs]
        basis_functions = [val[0] for val in bfs]
        surveys.append(Greedy_survey(basis_functions, weights, exptime=exptime, filtername=filtername,
                                     nside=nside, ignore_obs=ignore_obs, nexp=nexp,
                                     detailers=[detailer], **greed_survey_params))

    return surveys


def generate_blobs(nside, nexp=1, exptime=30., filter1s=['u', 'u', 'g', 'r', 'i', 'z', 'y'],
                   filter2s=['g', 'r', 'r', 'i', 'z', 'y', 'y'], pair_time=22.,
                   camera_rot_limits=[-80., 80.], n_obs_template=3,
                   season=300., season_start_hour=-4., season_end_hour=2.,
                   shadow_minutes=60., max_alt=76., moon_distance=30., ignore_obs='DD',
                   m5_weight=6., footprint_weight=0.6, slewtime_weight=3.,
                   stayfilter_weight=3., template_weight=12.):
    """
    Generate surveys that take observations in blobs.

    Parameters
    ----------
    nside : int (32)
        The HEALpix nside to use
    nexp : int (1)
        The number of exposures to use in a visit.
    exptime : float (30.)
        The exposure time to use per visit (seconds)
    filter1s : list of str
        The filternames for the first set
    filter2s : list of str
        The filter names for the second in the pair (None if unpaired)
    pair_time : float (22)
        The ideal time between pairs (minutes)
    camera_rot_limits : list of float ([-80., 80.])
        The limits to impose when rotationally dithering the camera (degrees).
    n_obs_template : int (3)
        The number of observations to take every season in each filter
    season : float (300)
        The length of season (i.e., how long before templates expire) (days)
    season_start_hour : float (-4.)
        For weighting how strongly a template image needs to be observed (hours)
    sesason_end_hour : float (2.)
        For weighting how strongly a template image needs to be observed (hours)
    shadow_minutes : float (60.)
        Used to mask regions around zenith (minutes)
    max_alt : float (76.
        The maximium altitude to use when masking zenith (degrees)
    moon_distance : float (30.)
        The mask radius to apply around the moon (degrees)
    ignore_obs : str or list of str ('DD')
        Ignore observations by surveys that include the given substring(s).
    m5_weight : float (3.)
        The weight for the 5-sigma depth difference basis function
    footprint_weight : float (0.3)
        The weight on the survey footprint basis function.
    slewtime_weight : float (3.)
        The weight on the slewtime basis function
    stayfilter_weight : float (3.)
        The weight on basis function that tries to stay avoid filter changes.
    template_weight : float (12.)
        The weight to place on getting image templates every season
    """

    blob_survey_params = {'slew_approx': 7.5, 'filter_change_approx': 140.,
                          'read_approx': 2., 'min_pair_time': 15., 'search_radius': 30.,
                          'alt_max': 85., 'az_range': 90., 'flush_time': 30.,
                          'smoothing_kernel': None, 'nside': nside, 'seed': 42, 'dither': True,
                          'twilight_scale': True}

    footprints = standard_goals(nside=nside)
    sum_footprints = 0
    for key in footprints:
        sum_footprints += np.sum(footprints[key])

    surveys = []

    times_needed = [pair_time, pair_time*2]
    for filtername, filtername2 in zip(filter1s, filter2s):
        detailer_list = []
        detailer_list.append(detailers.Camera_rot_detailer(min_rot=np.min(camera_rot_limits),
                                                           max_rot=np.max(camera_rot_limits)))
        detailer_list.append(detailers.Close_alt_detailer())
        # List to hold tuples of (basis_function_object, weight)
        bfs = []

        if filtername2 is not None:
            bfs.append((bf.M5_diff_basis_function(filtername=filtername, nside=nside), m5_weight/2.))
            bfs.append((bf.M5_diff_basis_function(filtername=filtername2, nside=nside), m5_weight/2.))

        else:
            bfs.append((bf.M5_diff_basis_function(filtername=filtername, nside=nside), m5_weight))

        if filtername2 is not None:
            bfs.append((bf.Footprint_basis_function(filtername=filtername,
                                                    footprint=footprints[filtername],
                                                    out_of_bounds_val=np.nan, nside=nside,
                                                    all_footprints_sum=sum_footprints), footprint_weight/2.))
            bfs.append((bf.Footprint_basis_function(filtername=filtername2,
                                                    footprint=footprints[filtername2],
                                                    out_of_bounds_val=np.nan, nside=nside,
                                                    all_footprints_sum=sum_footprints), footprint_weight/2.))
        else:
            bfs.append((bf.Footprint_basis_function(filtername=filtername,
                                                    footprint=footprints[filtername],
                                                    out_of_bounds_val=np.nan, nside=nside,
                                                    all_footprints_sum=sum_footprints), footprint_weight))

        bfs.append((bf.Slewtime_basis_function(filtername=filtername, nside=nside), slewtime_weight))
        bfs.append((bf.Strict_filter_basis_function(filtername=filtername), stayfilter_weight))

        if filtername2 is not None:
            bfs.append((bf.N_obs_per_year_basis_function(filtername=filtername, nside=nside,
                                                         footprint=footprints[filtername],
                                                         n_obs=n_obs_template, season=season,
                                                         season_start_hour=season_start_hour,
                                                         season_end_hour=season_end_hour), template_weight/2.))
            bfs.append((bf.N_obs_per_year_basis_function(filtername=filtername2, nside=nside,
                                                         footprint=footprints[filtername2],
                                                         n_obs=n_obs_template, season=season,
                                                         season_start_hour=season_start_hour,
                                                         season_end_hour=season_end_hour), template_weight/2.))
        else:
            bfs.append((bf.N_obs_per_year_basis_function(filtername=filtername, nside=nside,
                                                         footprint=footprints[filtername],
                                                         n_obs=n_obs_template, season=season,
                                                         season_start_hour=season_start_hour,
                                                         season_end_hour=season_end_hour), template_weight))
        # Masks, give these 0 weight
        bfs.append((bf.Zenith_shadow_mask_basis_function(nside=nside, shadow_minutes=shadow_minutes, max_alt=max_alt,
                                                         penalty=np.nan, site='LSST'), 0.))
        bfs.append((bf.Moon_avoidance_basis_function(nside=nside, moon_distance=moon_distance), 0.))
        filternames = [fn for fn in [filtername, filtername2] if fn is not None]
        bfs.append((bf.Filter_loaded_basis_function(filternames=filternames), 0))
        if filtername2 is None:
            time_needed = times_needed[0]
        else:
            time_needed = times_needed[1]
        bfs.append((bf.Time_to_twilight_basis_function(time_needed=time_needed), 0.))
        bfs.append((bf.Not_twilight_basis_function(), 0.))
        bfs.append((bf.Planet_mask_basis_function(nside=nside), 0.))

        # unpack the basis functions and weights
        weights = [val[1] for val in bfs]
        basis_functions = [val[0] for val in bfs]
        if filtername2 is None:
            survey_name = 'blob, %s' % filtername
        else:
            survey_name = 'blob, %s%s' % (filtername, filtername2)
        if filtername2 is not None:
            detailer_list.append(detailers.Take_as_pairs_detailer(filtername=filtername2))
        surveys.append(Blob_survey(basis_functions, weights, filtername1=filtername, filtername2=filtername2,
                                   exptime=exptime,
                                   ideal_pair_time=pair_time,
                                   survey_note=survey_name, ignore_obs=ignore_obs,
                                   nexp=nexp, detailers=detailer_list, **blob_survey_params))

    return surveys


def run_sched(surveys, survey_length=365.25, nside=32, fileroot='baseline_', verbose=False,
              extra_info=None, illum_limit=40.):
    years = np.round(survey_length/365.25)
    scheduler = Core_scheduler(surveys, nside=nside)
    n_visit_limit = None
    filter_sched = simple_filter_sched(illum_limit=illum_limit)
    observatory = Model_observatory(nside=nside)
    observatory, scheduler, observations = sim_runner(observatory, scheduler,
                                                      survey_length=survey_length,
                                                      filename=fileroot+'%iyrs.db' % years,
                                                      delete_past=True, n_visit_limit=n_visit_limit,
                                                      verbose=verbose, extra_info=extra_info,
                                                      filter_scheduler=filter_sched)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", dest='verbose', action='store_true')
    parser.set_defaults(verbose=False)
    parser.add_argument("--survey_length", type=float, default=365.25*10)
    parser.add_argument("--outDir", type=str, default="")
    parser.add_argument("--maxDither", type=float, default=0.7, help="Dither size for DDFs (deg)")
    parser.add_argument("--moon_illum_limit", type=float, default=40., help="illumination limit to remove u-band")

    args = parser.parse_args()
    survey_length = args.survey_length  # Days
    outDir = args.outDir
    verbose = args.verbose
    max_dither = args.maxDither
    illum_limit = args.moon_illum_limit

    nside = 32
    per_night = True  # Dither DDF per night
    nexp = 1  # All observations
    mixed_pairs = True  # For the blob scheduler
    camera_ddf_rot_limit = 75.

    extra_info = {}
    exec_command = ''
    for arg in sys.argv:
        exec_command += ' ' + arg
    extra_info['exec command'] = exec_command
    try:
        extra_info['git hash'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
    except subprocess.CalledProcessError:
        extra_info['git hash'] = 'Not in git repo'

    extra_info['file executed'] = os.path.realpath(__file__)

    fileroot = 'agnddf_'
    file_end = 'v1.5_'

    # Set up the DDF surveys to dither
    dither_detailer = detailers.Dither_detailer(per_night=per_night, max_dither=max_dither)
    details = [detailers.Camera_rot_detailer(min_rot=-camera_ddf_rot_limit, max_rot=camera_ddf_rot_limit), dither_detailer]
    ddfs = generate_dd_surveys(nside=nside, nexp=nexp, detailers=details)

    greedy = gen_greedy_surveys(nside, nexp=nexp)
    blobs = generate_blobs(nside, nexp=nexp)
    surveys = [ddfs, blobs, greedy]
    run_sched(surveys, survey_length=survey_length, verbose=verbose,
              fileroot=os.path.join(outDir, fileroot+file_end), extra_info=extra_info,
              nside=nside, illum_limit=illum_limit)
