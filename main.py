## imports
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from copy import deepcopy as dc

## notes
# 1 ha = 10,000 m2
# 1 sqft = 1/10.764 m2
# cost to reduce leakage 0.4 $/m3

## load data
data = pd.read_csv("data.csv", header=None)
params = pd.read_csv("params.csv", header=None)

## params
pop_gr = data[1][2] / 100
do = data[1][4]
hs_type = params.loc[0:5][1].values

## stats
stats = {}
stats["population"] = []

stats["water_resi_laundry"] = []
stats["water_resi_faucet"] = []
stats["water_resi_toilet"] = []
stats["water_resi_dishwash"] = []
stats["water_resi_shower"] = []
stats["water_resi_garden"] = []
stats["water_resi_leak"] = []

stats["water_nonresi_laundry"] = []
stats["water_nonresi_faucet"] = []
stats["water_nonresi_toilet"] = []
stats["water_nonresi_urinal"] = []
stats["water_nonresi_dishwash"] = []
stats["water_nonresi_shower"] = []
stats["water_nonresi_prerinse"] = []
stats["water_nonresi_coolheat"] = []
stats["water_nonresi_leak"] = []
stats["water_nonresi_foodice"] = []
stats["water_nonresi_park"] = []

stats["water_rainh_resi"] = []
stats["water_rainh_nonresi"] = []

stats["energy_dist"] = []
stats["energy_wwtreat"] = []
stats["energy_resi_heating"] = []
stats["energy_nonresi_heating"] = []

stats["carbon_pumping_hy"] = []
stats["carbon_treat_hy"] = []
stats["carbon_wwtrans_hy"] = []
stats["carbon_wwtreat_hy"] = []
stats["carbon_dist_hy"] = []

stats["carbon_pumping_pv"] = []
stats["carbon_treat_pv"] = []
stats["carbon_wwtrans_pv"] = []
stats["carbon_wwtreat_pv"] = []
stats["carbon_dist_pv"] = []

stats["water_final"] = []
stats["energy_final"] = []
stats["carbon_final"] = []

# previous year
prev_dwelling = [0,0,0,0,0]

## loop
for year in range(0,21):

    ## population
    pop = data[1][1] * (1+pop_gr)**year
    stats["population"].append(pop)

    household = pop / do
    household_add = 0
    if year == 0:
        h_sd = data[1][5] * household
        h_du = data[1][6] * household
        h_rh = data[1][7] * household
        h_sa = data[1][8] * household
        h_la = data[1][9] * household
        prev_dwelling = [h_sd, h_du, h_rh, h_sa, h_la]
    else:
        household_add = pop - (data[1][1] * (1+pop_gr)**(year-1))
        h_sd = prev_dwelling[0] + household_add * hs_type[0]
        h_du = prev_dwelling[1] + household_add * hs_type[1]
        h_rh = prev_dwelling[2] + household_add * hs_type[2]
        h_sa = prev_dwelling[3] + household_add * hs_type[3]
        h_la = prev_dwelling[4] + household_add * hs_type[4]
        prev_dwelling = [h_sd, h_du, h_rh, h_sa, h_la]


    ## residential
    area_total = data[1][0] * 10**6

    area_aver_res = data[1][10] / 10.764

    area_sd = h_sd * data[1][11] * 10**4
    area_sd_cover = area_sd * data[1][12]

    area_du = h_du * data[1][13] * 10**4
    area_du_cover = area_du * data[1][14]

    rh_area = data[1][15] * 10**4
    rh_tfa = data[1][17] * rh_area
    h_in_rh = rh_tfa / area_aver_res
    area_rh = h_rh / h_in_rh * rh_area
    area_rh_cover = area_rh * data[1][16]

    sa_area = data[1][18] * 10**4
    sa_tfa = data[1][20] * sa_area
    h_in_sa = sa_tfa / area_aver_res
    area_sa = h_sa / h_in_sa * sa_area
    area_sa_cover = area_sa * data[1][19]

    la_area = data[1][21] * 10**4
    la_tfa = data[1][23] * la_area
    h_in_la = la_tfa / area_aver_res
    area_la = h_la / h_in_la * la_area
    area_la_cover = area_la * data[1][22]

    area_residential = area_sd + area_du + area_rh + area_sa + area_la

    area_resi_cover = area_sd_cover + area_du_cover + area_rh_cover + area_sa_cover + area_la_cover
    area_resi_uncover = area_residential - area_resi_cover

    ## residential water
    if year == 0:
        garden_irg_rate = data[1][24]
        eff_faucet = data[1][32]
        eff_toilet = data[1][36]
        eff_shower = data[1][43]
        leakage_resi = data[1][47]
        rat_hot_ld = data[1][27]
        rat_hot_fa = data[1][34]
        rat_hot_sh = data[1][46]
    else:
        garden_irg_rate = params[1][5]
        eff_faucet = params[1][6]
        eff_toilet = params[1][7]
        eff_shower = params[1][8]
        leakage_resi = params[year][9]
        rat_hot_ld = params[year][10]
        rat_hot_fa = params[year][11]
        rat_hot_sh = params[year][12]

    irrigate_garden = garden_irg_rate / 264.2 * 10.764 # m3/m2/year
    w_garden = irrigate_garden * area_resi_uncover * data[1][241]

    w_laundry = data[1][25] * pop * 12 * data[1][26] / 1000
    w_faucet = data[1][31] * pop * 12 * eff_faucet / 1000
    w_toilet = data[1][35] * pop * 12 * eff_toilet / 1000
    w_dishwash = data[1][37] * pop * 12 * data[1][38] / 1000
    w_shower = data[1][42] * pop * 12 * data[1][44] * eff_shower / 1000

    w_indoor = w_laundry + w_faucet + w_toilet + w_dishwash + w_shower
    w_indoor_leak = w_indoor * leakage_resi
    w_outdoor_leak = w_garden * leakage_resi

    w_resi_indoor = w_indoor + w_indoor_leak
    w_resi_outdoor = w_garden + w_outdoor_leak

    w_resi = w_resi_indoor + w_resi_outdoor

    stats["water_resi_laundry"].append(w_laundry)
    stats["water_resi_faucet"].append(w_faucet)
    stats["water_resi_toilet"].append(w_toilet)
    stats["water_resi_dishwash"].append(w_dishwash)
    stats["water_resi_shower"].append(w_shower)
    stats["water_resi_garden"].append(w_garden)
    stats["water_resi_leak"].append(w_indoor_leak+w_outdoor_leak)

    # residential energy
    e_laundry = data[1][25] * pop * 12 * data[1][28]
    e_laundry_sb = w_laundry * rat_hot_ld * data[1][29] * data[1][30] * 1000
    e_faucet = w_faucet * rat_hot_fa * data[1][33] * 1000
    e_dishwash = data[1][37] * pop * 12 * data[1][39] * data[1][40]
    e_dishwash_heat = e_dishwash * data[1][41]
    e_shower = w_shower * rat_hot_sh * data[1][45] * 1000

    e_resi = e_laundry + e_laundry_sb + e_faucet + e_dishwash + e_shower

    ## non residential
    if year == 0:
        park_irg_rate = data[1][54]
        eff_nr_faucet = data[1][100]
        eff_nr_toilet = data[1][109]
        eff_nr_shower = data[1][126]
        leak_reduc = 0
    else:
        park_irg_rate = params[1][13]
        eff_nr_faucet = params[1][21]
        eff_nr_toilet = params[1][22]
        eff_nr_shower = params[1][23]
        leak_reduc = params[year][24]

    irrigate_park = park_irg_rate / 264.2 * 10.764 # m3/m2/year

    area_park = data[1][55] * 10**4 + household_add * data[1][56] / 1000

    area_aver_commer = data[1][58] * 10**4
    area_aver_commer_cover = data[1][59]

    area_aver_inst = data[1][61] * 10**4
    area_aver_inst_cover = data[1][62]

    area_aver_ind = data[1][64] * 10**4
    area_aver_ind_cover = data[1][65]

    area_commer = data[1][67]

    area_restaurant = area_commer * data[1][68] * (1+params[1][14]/1000)**year
    area_office = area_commer * data[1][69] * (1+params[1][15]/1000)**year
    area_supermarket = area_commer * data[1][70] * (1+params[1][16]/1000)**year

    area_ind = data[1][74] * (1+params[1][17]/1000)**year

    init_hotel = data[1][76] * (1+params[1][18]/1000)**year
    init_hospital = data[1][78] * (1+params[1][19]/1000)**year
    init_school = data[1][80] * (1+params[1][20]/1000)**year

    floor_hotel = init_hotel * data[1][82]
    floor_hospital = init_hospital * data[1][83]
    floor_school = init_school * data[1][84]

    area_hotel = floor_hotel / 10.764 / data[1][63]
    area_hospital = floor_hospital / 10.764 / data[1][63]
    area_school = floor_school / 10.764 / data[1][63]

    # non resi laundry
    freq_restaurant_laundry = data[1][85] * 12 * area_restaurant
    freq_hotel_laundry = data[1][86] * 12 * init_hotel
    freq_office_laundry = data[1][87] * 12 * area_office
    freq_hospital_laundry = data[1][88] * 12 * init_hospital
    freq_ind_laundry = data[1][89] * 12 * area_ind
    freq_school_laundry = data[1][90] * 12 * init_school
    freq_supermarket_laundry = data[1][91] * 12 * area_supermarket

    w_nr_laundry = (freq_restaurant_laundry + freq_hotel_laundry + freq_office_laundry + freq_hospital_laundry
                    + freq_ind_laundry + freq_school_laundry + freq_supermarket_laundry) * data[1][92] / 1000

    # non resi faucet
    freq_restaurant_faucet = data[1][93] * 12 * area_restaurant
    freq_hotel_faucet = data[1][94] * 12 * init_hotel
    freq_office_faucet = data[1][95] * 12 * area_office
    freq_hospital_faucet = data[1][96] * 12 * init_hospital
    freq_ind_faucet = data[1][97] * 12 * area_ind
    freq_school_faucet = data[1][98] * 12 * init_school
    freq_supermarket_faucet = data[1][99] * 12 * area_supermarket

    w_nr_faucet = (freq_restaurant_faucet + freq_hotel_faucet + freq_office_faucet + freq_hospital_faucet
                   + freq_ind_faucet + freq_school_faucet + freq_supermarket_faucet) * data[1][100] / 1000 / data[1][101]

    # non resi toilet
    freq_restaurant_toilet = data[1][102] * 12 * area_restaurant
    freq_hotel_toilet = data[1][103] * 12 * init_hotel
    freq_office_toilet = data[1][104] * 12 * area_office
    freq_hospital_toilet = data[1][105] * 12 * init_hospital
    freq_ind_toilet = data[1][106] * 12 * area_ind
    freq_school_toilet = data[1][107] * 12 * init_school
    freq_supermarket_toilet = data[1][108] * 12 * area_supermarket

    w_nr_toilet = (freq_restaurant_toilet + freq_hotel_toilet + freq_office_toilet + freq_hospital_toilet
                   + freq_ind_toilet + freq_school_toilet + freq_supermarket_toilet) * data[1][109] / 1000

    # non resu urinal
    freq_restaurant_urinal = data[1][111] * 12 * area_restaurant
    freq_hotel_urinal = data[1][112] * 12 * init_hotel
    freq_office_urinal = data[1][113] * 12 * area_office
    freq_hospital_urinal = data[1][114] * 12 * init_hospital
    freq_ind_urinal = data[1][115] * 12 * area_ind
    freq_school_urinal = data[1][116] * 12 * init_school
    freq_supermarket_urinal = data[1][117] * 12 * area_supermarket

    w_nr_urinal = (freq_restaurant_urinal + freq_hotel_urinal + freq_office_urinal + freq_hospital_urinal
                   + freq_ind_urinal + freq_school_urinal + freq_supermarket_urinal) * data[1][110] / 1000

    # non resi dishwasher
    freq_restaurant_dishwasher = data[1][118] * 12 * area_restaurant
    freq_hotel_dishwasher = data[1][119] * 12 * init_hotel
    freq_office_dishwasher = data[1][120] * 12 * area_office
    freq_hospital_dishwasher = data[1][121] * 12 * init_hospital
    freq_ind_dishwasher = data[1][122] * 12 * area_ind
    freq_school_dishwasher = data[1][123] * 12 * floor_school
    freq_supermarket_dishwasher = data[1][124] * 12 * area_supermarket

    w_nr_dishwasher = (freq_restaurant_dishwasher + freq_hotel_dishwasher + freq_office_dishwasher
                       + freq_hospital_dishwasher + freq_ind_dishwasher + freq_school_dishwasher
                       + freq_supermarket_dishwasher) * data[1][125] / 1000

    # non resi shower
    freq_restaurant_shower = data[1][128] * 12 * area_restaurant
    freq_hotel_shower = data[1][129] * 12 * init_hotel
    freq_office_shower = data[1][130] * 12 * area_office
    freq_hospital_shower = data[1][131] * 12 * init_hospital
    freq_ind_shower = data[1][132] * 12 * area_ind
    freq_school_shower = data[1][133] * 12 * init_school
    freq_supermarket_shower = data[1][134] * 12 * area_supermarket

    w_nr_shower = (freq_restaurant_shower + freq_hotel_shower + freq_office_shower + freq_hospital_shower
                   + freq_ind_shower + freq_school_shower + freq_supermarket_shower) * data[1][126] / 1000 / data[1][127]

    # non resi pre rinse
    freq_restaurant_prerinse = data[1][136] * 12 * area_restaurant
    freq_hotel_prerinse = data[1][137] * 12 * init_hotel
    freq_office_prerinse = data[1][138] * 12 * area_office
    freq_hospital_prerinse = data[1][139] * 12 * init_hospital
    freq_ind_prerinse = data[1][140] * 12 * area_ind
    freq_school_prerinse = data[1][141] * 12 * floor_school
    freq_supermarket_prerinse = data[1][142] * 12 * area_supermarket

    w_nr_prerinse = (freq_restaurant_prerinse + freq_hotel_prerinse + freq_office_prerinse + freq_hospital_prerinse
                   + freq_ind_prerinse + freq_school_prerinse + freq_supermarket_prerinse) * data[1][135] / 1000

    # cooling heating
    freq_restaurant_cohe = data[1][143] * 12 * area_restaurant
    freq_hotel_cohe = data[1][144] * 12 * init_hotel
    freq_office_cohe = data[1][145] * 12 * area_office
    freq_hospital_cohe = data[1][146] * 12 * init_hospital
    freq_ind_cohe = data[1][147] * 12 * area_ind
    freq_school_cohe = data[1][148] * 12 * init_school
    freq_supermarket_cohe = data[1][149] * 12 * area_supermarket

    w_nr_cohe = (freq_restaurant_cohe + freq_hotel_cohe + freq_office_cohe + freq_hospital_cohe
                   + freq_ind_cohe + freq_school_cohe + freq_supermarket_cohe) / 1000

    # nr leakage
    freq_restaurant_leak = data[1][150] * 12 * area_restaurant
    freq_hotel_leak = data[1][151] * 12 * init_hotel
    freq_office_leak = data[1][152] * 12 * area_office
    freq_hospital_leak = data[1][153] * 12 * init_hospital
    freq_ind_leak = data[1][154] * 12 * area_ind
    freq_school_leak = data[1][155] * 12 * init_school
    freq_supermarket_leak = data[1][156] * 12 * area_supermarket

    w_nr_leak = (freq_restaurant_leak + freq_hotel_leak + freq_office_leak + freq_hospital_leak
                   + freq_ind_leak + freq_school_leak + freq_supermarket_leak) / 1000 * (1 - leak_reduc)

    # nr food prep and ice
    freq_restaurant_foodice = data[1][157] * 12 * area_restaurant
    freq_hotel_foodice = data[1][158] * 12 * init_hotel
    freq_office_foodice = data[1][159] * 12 * area_office
    freq_hospital_foodice = data[1][160] * 12 * init_hospital
    freq_ind_foodice = data[1][161] * 12 * area_ind
    freq_school_foodice = data[1][162] * 12 * init_school
    freq_supermarket_foodice = data[1][163] * 12 * area_supermarket

    w_nr_foodice = (freq_restaurant_foodice + freq_hotel_foodice + freq_office_foodice + freq_hospital_foodice
                   + freq_ind_foodice + freq_school_foodice + freq_supermarket_foodice) / 1000

    # park irrigation
    w_nr_park = area_park * irrigate_park * data[1][242]

    # non resi water
    w_nr = (w_nr_laundry + w_nr_faucet + w_nr_toilet + w_nr_urinal + w_nr_dishwasher + w_nr_shower + w_nr_prerinse
            + w_nr_cohe + w_nr_leak + w_nr_foodice) + w_nr_park

    stats["water_nonresi_laundry"].append(w_nr_laundry)
    stats["water_nonresi_faucet"].append(w_nr_faucet)
    stats["water_nonresi_toilet"].append(w_nr_toilet)
    stats["water_nonresi_urinal"].append(w_nr_urinal)
    stats["water_nonresi_dishwash"].append(w_nr_dishwasher)
    stats["water_nonresi_shower"].append(w_nr_shower)
    stats["water_nonresi_prerinse"].append(w_nr_prerinse)
    stats["water_nonresi_coolheat"].append(w_nr_cohe)
    stats["water_nonresi_leak"].append(w_nr_leak)
    stats["water_nonresi_foodice"].append(w_nr_foodice)
    stats["water_nonresi_park"].append(w_nr_park)

    ## non resi energy
    e_nr_heating_laundry = w_nr_laundry / data[1][92] * 1000 * data[1][165] * data[1][164]
    e_nr_heating_faucet = w_nr_faucet * 1000 * data[1][167] * data[1][166]
    e_nr_dishwasher_heating = w_nr_dishwasher / (data[1][125] / 1000) * data[1][168]
    e_nr_shower = w_nr_shower * 1000 * data[1][171] * data[1][170]
    e_nr_prerinse = w_nr_prerinse * 1000 * data[1][173] * data[1][172]

    ## rainfall harvesting
    roof_commer = area_commer / 10.764 * area_aver_commer_cover
    roof_institutional = (area_hotel + area_hospital + area_school) * area_aver_inst_cover
    roof_ind = area_ind / 10.764  * area_aver_ind_cover

    rainfall = data[1][174] / 1000

    if year == 0:
        rainh_resi = data[1][175]
        rainh_nonresi = data[1][175]

    else:
        rainh_resi = params[year][44]
        rainh_nonresi = params[year][45]

    w_rainh_resi = rainfall * 12 * area_resi_cover * rainh_resi
    w_rainh_nonresi = rainfall * 12 * (roof_commer + roof_institutional + roof_ind) * rainh_nonresi

    stats["water_rainh_resi"].append(w_rainh_resi)
    stats["water_rainh_nonresi"].append(w_rainh_nonresi)

    ##
    w_need = w_resi + w_nr - (w_rainh_resi*(1+leakage_resi)) - w_rainh_nonresi

    ## electricity
    if year == 0:
        pumping_pow = [data[1][182], data[1][183]]
        wtreat_pow = [data[1][184], data[1][185]]
        wwtrans_pow = [data[1][186], data[1][187]]
        wwtreat_pow = [data[1][188], data[1][189]]
        resi_hot_pow = [data[1][192], data[1][193], data[1][194], data[1][195], data[1][196]]
        nonresi_hot_pow = [data[1][197], data[1][198], data[1][199], data[1][200], data[1][201]]
        infil_reduc = 0
    else:
        pumping_pow = [params[year][25], params[year][26]]
        wtreat_pow = [params[year][27], params[year][28]]
        wwtrans_pow = [params[year][29], params[year][30]]
        wwtreat_pow = [params[year][31], params[year][32]]
        resi_hot_pow = [params[year][33], params[year][34], params[year][35], params[year][36], params[year][37]]
        nonresi_hot_pow = [params[year][38], params[year][39], params[year][40], params[year][41], params[year][42]]
        infil_reduc = params[year][43]

    cf_hy = data[1][176]
    cf_st = data[1][177]
    cf_spv = data[1][178]
    cf_ng = data[1][179]
    cf_o = data[1][180]
    cf_p = data[1][181]

    e_pumping = w_need * data[1][48] * 1000
    cf_pumping_hy = e_pumping * pumping_pow[0] * cf_hy
    cf_pumping_pv = e_pumping * pumping_pow[1] * cf_spv

    e_treat = w_need * data[1][49] * 1000
    cf_treat_hy = e_treat * wtreat_pow[0] * cf_hy
    cf_treat_pv = e_treat * wtreat_pow[1] * cf_spv

    infil = data[1][233] / 1000 * 365 * pop * (1 - infil_reduc)
    wastewater = w_need - w_indoor_leak - w_outdoor_leak - w_nr_leak - w_garden - w_nr_park

    e_ww_transport = (wastewater + infil) * data[1][51] * 1000
    cf_ww_transport_hy = e_ww_transport * wwtrans_pow[0] * cf_hy
    cf_ww_transport_pv = e_ww_transport * wwtrans_pow[1] * cf_spv

    e_ww_treatment= (wastewater + infil) * data[1][52] * 1000
    cf_ww_treatment_hy = e_ww_treatment * wwtreat_pow[0] * cf_hy
    cf_ww_treatment_pv = e_ww_treatment * wwtreat_pow[1] * cf_spv

    cf_dist_hy = cf_pumping_hy + cf_treat_hy + cf_ww_transport_hy + cf_ww_treatment_hy
    cf_dist_pv = cf_pumping_pv + cf_treat_pv + cf_ww_transport_pv + cf_ww_treatment_pv

    stats["carbon_pumping_hy"].append(cf_pumping_hy)
    stats["carbon_treat_hy"].append(cf_pumping_hy)
    stats["carbon_wwtrans_hy"].append(cf_pumping_hy)
    stats["carbon_wwtreat_hy"].append(cf_pumping_hy)
    stats["carbon_dist_hy"].append(cf_dist_hy)
    
    if year == 0:
        stats["carbon_pumping_pv"].append(cf_pumping_pv)
        stats["carbon_treat_pv"].append(cf_treat_pv)
        stats["carbon_wwtrans_pv"].append(cf_ww_transport_pv)
        stats["carbon_wwtreat_pv"].append(cf_ww_treatment_pv)
        stats["carbon_dist_pv"].append(cf_dist_pv)
    else:
        stats["carbon_pumping_pv"].append(cf_pumping_pv - sum(stats["carbon_pumping_pv"]))
        stats["carbon_treat_pv"].append(cf_treat_pv - sum(stats["carbon_treat_pv"]))
        stats["carbon_wwtrans_pv"].append(cf_ww_transport_pv - sum(stats["carbon_wwtrans_pv"]))
        stats["carbon_wwtreat_pv"].append(cf_ww_treatment_pv - sum(stats["carbon_wwtreat_pv"]))
        stats["carbon_dist_pv"].append(cf_dist_pv - sum(stats["carbon_dist_pv"]))

    cf_pumping = stats["carbon_pumping_hy"][year] + stats["carbon_pumping_pv"][year]
    cf_treat = stats["carbon_treat_hy"][year] + stats["carbon_treat_pv"][year]
    cf_ww_transport = stats["carbon_wwtrans_hy"][year] + stats["carbon_wwtrans_pv"][year]
    cf_ww_treatment = stats["carbon_wwtreat_hy"][year] + stats["carbon_wwtreat_pv"][year]

    # heating
    e_resi_nonheating = e_laundry + e_dishwash
    e_resi_heating = e_laundry_sb + e_faucet + e_shower
    e_nr_nonheating = e_nr_dishwasher_heating
    e_nr_heating = e_nr_heating_laundry + e_nr_heating_faucet + e_nr_shower + e_nr_prerinse

    cf_resi_heating = e_resi_heating * (resi_hot_pow[0] * cf_hy + resi_hot_pow[1] * cf_st
                                        + resi_hot_pow[2] * cf_ng + resi_hot_pow[3]  * cf_o
                                        + resi_hot_pow[4] * cf_p)

    cf_nr_heating = e_nr_heating * (nonresi_hot_pow[0] * cf_hy + nonresi_hot_pow[1] * cf_st
                                    + nonresi_hot_pow[2] * cf_ng + nonresi_hot_pow[3]  * cf_o
                                    + nonresi_hot_pow[4] * cf_p)

    # electrical wf
    wf_hy = data[1][202] / 1000 * (e_pumping * pumping_pow[0] + e_treat * wtreat_pow[0]
                                   + e_ww_transport * wwtrans_pow[0] + e_ww_treatment * wwtreat_pow[0]
                                   + e_resi_heating * resi_hot_pow[0] + e_nr_heating * nonresi_hot_pow[0])

    wf_st = data[1][203] / 1000 * (e_resi_heating * resi_hot_pow[1] + e_nr_heating * nonresi_hot_pow[1])

    wf_spv = data[1][204] / 1000 * (e_pumping * pumping_pow[1] + e_treat * wtreat_pow[1]
                                    + e_ww_transport * wwtrans_pow[1] + e_ww_treatment * wwtreat_pow[1])

    wf_ng = data[1][205] / 1000 * (e_resi_heating * resi_hot_pow[2] + e_nr_heating * nonresi_hot_pow[2])

    wf_o = data[1][206] / 1000 * (e_resi_heating * resi_hot_pow[3] + e_nr_heating * nonresi_hot_pow[3])

    wf_p = data[1][207] / 1000 * (e_resi_heating * resi_hot_pow[4] + e_nr_heating * nonresi_hot_pow[4])

    wf_electrical = wf_hy + wf_st + wf_spv + wf_ng + wf_o + wf_p

    ## treatment
    wf_chlor_wt = (data[1][208] * w_need + data[1][211] * (wastewater + infil)) * 1000 * data[1][214]
    wf_pac_wt = (data[1][209] * w_need + data[1][212] * (wastewater + infil)) * 1000 * data[1][215]
    wf_pol_wt = (data[1][210] * w_need + data[1][213] * (wastewater + infil)) * 1000 * data[1][216]

    cf_chlor_wt = (data[1][208] * w_need + data[1][211] * (wastewater + infil)) * 1000 * data[1][217]
    cf_pac_wt = (data[1][209] * w_need + data[1][212] * (wastewater + infil)) * 1000 * data[1][218]
    cf_pol_wt = (data[1][210] * w_need + data[1][213] * (wastewater + infil)) * 1000 * data[1][219]

    ee_chlor_wt = (data[1][208] * w_need + data[1][211] * (wastewater + infil)) * 1000 * data[1][220]
    ee_pac_wt = (data[1][209] * w_need + data[1][212] * (wastewater + infil)) * 1000 * data[1][221]
    ee_pol_wt = (data[1][210] * w_need + data[1][213] * (wastewater + infil)) * 1000 * data[1][222]

    biosolids = (wastewater + infil) * data[1][223] * 1000

    fuel_transport = data[1][225] * (biosolids * data[1][224]) * data[1][226]
    e_sludge_trans = fuel_transport * data[1][227]

    cf_sludge_trans = e_sludge_trans * data[1][228]
    wf_sludge_trans = e_sludge_trans * data[1][229] / 1000

    wf_treatment = wf_chlor_wt + wf_pac_wt + wf_pol_wt + wf_sludge_trans
    e_treatment = e_ww_transport + e_ww_treatment + ee_chlor_wt + ee_pac_wt + ee_pol_wt + e_sludge_trans
    e_dist = e_pumping + e_treat

    cf_total = (cf_pumping + cf_treat + cf_ww_transport + cf_ww_treatment + cf_resi_heating + cf_nr_heating
                + cf_chlor_wt + cf_pac_wt + cf_pol_wt + cf_sludge_trans)

    ## totals
    t_water = w_need + wf_electrical + wf_treatment
    t_energy = e_resi_nonheating + e_resi_heating + e_nr_nonheating + e_nr_heating + e_treatment + e_dist
    t_carbon = cf_total

    stats["energy_dist"].append(e_dist)
    stats["energy_wwtreat"].append(e_treatment)
    stats["energy_resi_heating"].append(e_resi_heating)
    stats["energy_nonresi_heating"].append(e_nr_heating)

    stats["water_final"].append(t_water)
    stats["energy_final"].append(t_energy)
    stats["carbon_final"].append(t_carbon)

aa_stats = pd.DataFrame(stats)

aa_stats['WF'] = aa_stats["water_final"] / aa_stats["population"]
aa_stats['EF'] = aa_stats["energy_final"] / aa_stats["population"]
aa_stats['CF'] = aa_stats["carbon_final"] / aa_stats["population"]

## footprint calc
years = np.arange(0,21, dtype='int')

plt.rc('font', family='serif')

fig, ax = plt.subplots(figsize=(10,6))

ax.plot(years, aa_stats["water_final"], color='blue')
ax2 = ax.twinx()
ax2.plot(years, aa_stats["WF"], color='blue', ls='none', marker='x')

ax.set_xticks(years)
ax.set_xlabel('Year')
ax.set_ylabel('Water Usage (m$^3$)')
ax2.set_ylabel('Water Footprint (m$^3$/capita)')
ax.grid()

fig, ax = plt.subplots(figsize=(10,6))

ax.plot(years, aa_stats["energy_final"], color='orange')
ax2 = ax.twinx()
ax2.plot(years, aa_stats["EF"], color='orange', ls='none', marker='x')

ax.set_xticks(years)
ax.set_xlabel('Year')
ax.set_ylabel('Energy Usage (kWh)')
ax2.set_ylabel('Energy Footprint (kWh/capita)')
ax.grid()

fig, ax = plt.subplots(figsize=(10,6))

ax.plot(years, aa_stats["carbon_final"], color='green')
ax2 = ax.twinx()
ax2.plot(years, aa_stats["CF"], color='green', ls='none', marker='x')

ax.set_xticks(years)
ax.set_xlabel('Year')
ax.set_ylabel('Carbon Emission (kgCO2)')
ax2.set_ylabel('Carbon Footprint (kgCO2/capita)')
ax.grid()

##
print_sheet = aa_stats.to_csv("result.csv")
