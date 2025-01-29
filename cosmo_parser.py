#https://data.geo.admin.ch/ch.meteoschweiz.prognosen/punktprognosen/Legende_COSMO-E_all_stations.txt #fielname = legend + '_' + member_id
import csv
from io import StringIO
import numpy, urllib.request
from datetime import datetime, timedelta

URL_COSMO = 'https://data.geo.admin.ch/ch.meteoschweiz.prognosen/punktprognosen/COSMO-E-all-stations.csv'
def create_cosmo_errored_file():
    abr_list = ['ARO', 'RAG', 'HAI', 'HLL', 'DEM', 'EBK', 'ELM', 'EIN', 'ANT', 'MER', 'CHD', 'GRA', 'CHM', 'LAG', 'KOP', 'GRC', 'BLA', 'GRO', 'BEH', 'SIA', 'SMM', 'DAV', 'CHU', 'ROB', 'SAM', 'SCU', 'DOL', 'PAY', 'JUN', 'WYN', 'SAE', 'VAD', 'AIG', 'MLS', 'FAH', 'MVE', 'ZER', 'CHA', 'PIL', 'ALT', 'ULR', 'PIO', 'LUG', 'NAP', 'SIO', 'MAG', 'NEU', 'SBO', 'INT', 'DIS', 'STG', 'GLA', 'GVE', 'KLO', 'GUE', 'PUY', 'GSB', 'ABO', 'VIS', 'CDF', 'RUE', 'BUS', 'LUZ', 'ENG', 'SHA', 'SMA', 'SBE', 'WFJ', 'COV', 'BAS', 'CGI', 'FRE', 'BER', 'GUT', 'GOE', 'WAE', 'TAE', 'REH', 'OTL', 'BEZ', 'MUB', 'CIM', 'EVO', 'LEI', 'GRH', 'COM', 'LAE', 'HOE', 'PLF', 'ROE', 'PSI', 'BIN', 'MRP', 'MAR', 'MSK', 'SAG', 'CHZ', 'STC', 'COY', 'VEV', 'BOU', 'TIT', 'FRU', 'MOE', 'MAH', 'CHB', 'MTE', 'PRE', 'VLS', 'ARH', 'UEB', 'GOS', 'AND', 'BIV', 'MTR', 'BIA', 'SCM', 'AEG', 'LAT', 'CDM', 'BUF', 'ILZ', 'BIZ', 'LAC', 'FLU', 'BOL', 'THU', 'MAS', 'BRN', 'VIT', 'GRE', 'MOA', 'CEV', 'CRM', 'CMA', 'GEN', 'BIE', 'ORO', 'BRL', 'BAN', 'EGO', 'STK', 'DIA', 'BRZ', 'SPF', 'QUI', 'VAB', 'PMA', 'NAS', 'ATT', 'EVI', 'GOR', 'EGH', 'GIH', 'ALP', 'GES', 'SRS', 'VIO', 'DLSTU', 'OSFEK', 'OBR', 'TSG', 'ARD', 'FRSTR', 'FRBES', 'MOB', 'SIM', 'LMA', 'MEE', 'PAA', 'SIR', 'OSGAN', 'OSVER', 'OSFOR', 'OSLAU', 'OSTHU', 'OSFAS', 'OSINL', 'DUB', 'BUO', 'EMM', 'DLMUN', 'AGN']
    with open('COSMO-E-all-stations.csv', 'w') as file:
        now = datetime.now() - timedelta(days=1)
        now_rounded = now - timedelta(hours=now.hour % 6 +6, minutes=now.minute)
        print(now_rounded)
        end_time = now_rounded + timedelta(days=6)
        text_to_add = f'''MeteoSchweiz / MeteoSuisse / MeteoSvizzera / MeteoSwiss
    Date_of_production:;{now.strftime("%Y-%m-%d")};
    File_type:;ASCII_TABLE;1.0;

    Model_name:;icon-ch2-eps;
    Type_of_product:;icon-ch2-eps_individual_ensemble_member;
    Total_number_of_members_in_file:;21;
    Initial_time:;{now.strftime("%Y-%m-%d")};{now_rounded.strftime("%H:%M")};+0:00;
    Start_time:;{now.strftime("%Y-%m-%d")};{now_rounded.strftime("%H:%M")};+0:00;
    End_time:;{end_time.strftime("%Y-%m-%d")};{now_rounded.strftime("%H:%M")};+0:00;

    Missing_value_code:;-999.0;
    Data_separator:;";";
    Number_of_data_columns:;126;
    Number_of_data_rows:;3843;
    Number_of_data_header_rows:;3;

    Indicator:;ARO;RAG;HAI;HLL;DEM;EBK;ELM;EIN;ANT;MER;CHD;GRA;CHM;LAG;KOP;GRC;BLA;GRO;BEH;SIA;SMM;DAV;CHU;ROB;SAM;SCU;DOL;PAY;JUN;WYN;SAE;VAD;AIG;MLS;FAH;MVE;ZER;CHA;PIL;ALT;ULR;PIO;LUG;NAP;SIO;MAG;NEU;SBO;INT;DIS;STG;GLA;GVE;KLO;GUE;PUY;GSB;ABO;VIS;CDF;RUE;BUS;LUZ;ENG;SHA;SMA;SBE;WFJ;COV;BAS;CGI;FRE;BER;GUT;GOE;WAE;TAE;REH;OTL;BEZ;MUB;CIM;EVO;LEI;GRH;COM;LAE;HOE;PLF;ROE;PSI;BIN;MRP;MAR;MSK;SAG;CHZ;STC;COY;VEV;BOU;TIT;FRU;MOE;MAH;CHB;MTE;PRE;VLS;ARH;UEB;GOS;AND;BIV;MTR;BIA;SCM;AEG;LAT;CDM;BUF;ILZ;BIZ;LAC;FLU;BOL;THU;MAS;BRN;VIT;GRE;MOA;CEV;CRM;CMA;GEN;BIE;ORO;BRL;BAN;EGO;STK;DIA;BRZ;SPF;QUI;VAB;PMA;NAS;ATT;EVI;GOR;EGH;GIH;ALP;GES;SRS;VIO;DLSTU;OSFEK;OBR;TSG;ARD;FRSTR;FRBES;MOB;SIM;LMA;MEE;PAA;SIR;OSGAN;OSVER;OSFOR;OSLAU;OSTHU;OSFAS;OSINL;DUB;BUO;EMM;DLMUN;AGN;
    Grid_longitude:;9.682441;9.477546;9.040956;8.452563;7.372132;9.086511;9.183060;8.746970;8.580873;8.183796;7.118774;7.132603;6.996567;7.781869;7.600197;7.798687;7.796596;9.150620;10.032224;9.745399;10.453267;9.868561;9.545574;10.051627;9.865728;10.299841;6.116150;6.908478;8.013212;7.812535;9.362368;9.501072;6.916560;7.017713;6.944203;7.450724;7.763168;7.043646;8.241209;8.621592;8.298104;8.727744;8.954651;7.940687;7.297746;8.924325;6.937901;8.959135;7.844364;8.892683;9.442170;9.062386;6.128136;8.549488;8.650539;6.650367;7.132428;7.565800;7.822523;6.773959;7.919212;8.060222;8.328531;8.364555;8.638144;8.618613;9.202569;9.804056;9.815635;7.597009;6.222195;6.542294;7.466152;9.292926;7.970281;8.768583;8.895643;8.544215;8.745980;8.234138;7.239880;8.782514;7.518407;8.173220;8.372540;8.940198;8.377089;8.974022;7.298824;8.538796;8.234138;8.156863;7.803030;7.022213;7.273891;8.637753;8.463399;7.706701;7.117671;6.861665;6.887074;8.459070;7.686863;7.865450;6.564634;6.305486;7.581596;6.426712;9.191792;9.578052;8.489507;8.591431;9.422447;9.648900;8.896598;8.989841;8.958728;8.563948;9.723203;7.094212;10.242110;9.238325;9.243321;8.907515;8.010183;7.433610;7.607428;7.077156;7.490913;6.731043;7.425372;8.246100;8.614338;7.057538;9.210239;9.019965;6.350988;6.878308;6.577694;7.538532;8.020725;8.980531;7.232578;8.052541;8.003057;9.261654;9.548582;9.493205;10.241860;7.313248;7.026470;7.828852;8.095775;8.170508;8.269591;8.565689;9.640654;9.580988;9.223239;9.595859;9.619730;9.637395;9.682441;7.614439;6.019038;7.193166;8.091125;8.886485;8.078847;6.924338;7.297746;10.015366;10.041587;9.948621;9.885118;9.772999;9.895441;9.713336;8.623934;8.378124;8.300118;11.808451;8.885913;
    Grid_latitude:;46.791271;47.033257;47.655197;47.675144;47.368526;47.290199;46.919579;47.140797;46.632942;46.724045;46.458328;46.766037;47.066689;46.946609;47.119686;46.170345;46.416260;46.252361;46.396557;46.421150;46.623539;46.843109;46.885731;46.323666;46.511868;46.792877;46.429527;46.810989;46.544617;47.265610;47.233047;47.139359;46.338173;46.512573;47.436375;46.318501;46.028427;47.127758;46.971977;46.887505;46.500572;46.501625;46.011642;47.004803;46.217503;46.165852;46.995209;45.859951;46.680119;46.719097;47.425961;47.049160;46.254696;47.457859;46.664452;46.507824;45.877449;46.502796;46.302261;47.068562;47.440125;47.392761;47.040340;46.844227;47.660995;47.377514;46.447678;46.838905;46.408470;47.525620;46.403179;46.831215;46.989799;47.601383;47.366604;47.246681;47.500118;47.431396;46.182262;47.572784;46.966953;46.232681;46.078903;47.593655;46.558670;46.466473;47.482147;47.337284;46.717831;46.421326;47.572784;46.388336;45.993462;46.150452;46.948849;47.101654;47.212051;47.566177;47.186794;46.453053;46.382477;46.761379;46.622036;47.556126;46.734673;46.658535;46.175972;46.482986;46.616127;47.484238;47.344311;46.685856;46.616066;46.479843;46.432663;46.305538;47.214870;47.155720;46.646088;46.369118;46.662903;46.785019;47.497963;47.197369;46.925114;46.644962;46.740128;46.652447;46.918827;46.619492;47.184410;47.244808;46.301552;47.046726;46.873871;45.929863;46.534100;46.558262;46.999428;46.979683;47.181381;47.676712;46.322796;46.755890;46.941368;47.112408;46.733696;46.603775;46.815567;46.093872;46.176758;45.991207;46.452171;46.848396;46.926857;46.978157;46.979565;46.340164;48.681519;47.276485;47.382610;46.800934;46.791271;48.538441;47.252956;46.085892;46.179382;46.158577;46.753582;46.847687;46.217503;46.996765;46.950584;47.188259;47.075043;47.189392;47.280392;47.254795;47.403980;46.966347;47.085476;48.351383;45.980492;
    Grid_idx:;143568;196097;197347;153892;194098;196183;195899;196790;190235;193007;193384;191877;185674;191103;191276;192278;192692;189998;142924;142749;145620;143516;143599;139638;143285;145209;184734;185262;192840;194781;197560;197473;183699;183807;148106;193331;193199;185707;194422;196932;190440;190225;189726;191049;193434;190157;185392;189627;192812;195717;197587;196339;182821;196499;195150;184013;193971;192144;192312;185526;194673;194631;194522;197118;197163;196504;195503;143518;143364;150893;184639;183898;191645;197822;194644;196758;197228;196493;190564;195024;191503;190178;193670;195013;190347;195339;195033;196867;191921;190619;195024;192520;193185;193540;191500;196634;196624;150913;185736;183753;183730;195123;192610;151079;183911;184495;193786;184415;195647;197639;196590;195267;195588;142843;190040;190134;196834;196631;143208;193409;145561;195912;197784;196832;191170;191809;191574;185188;191654;183974;191417;194578;190635;185687;196026;189765;184434;183849;185565;191639;194759;197358;193455;192968;191171;196132;143440;143228;145214;193701;193538;193187;192522;190988;194407;197032;143642;142809;268736;145893;145941;143560;143568;154111;147799;193585;192398;190188;192974;185239;193434;145090;145081;145805;145122;145881;145825;145848;196526;197087;194527;228469;189515;
    Grid_height:;1847.2;499.4;668.9;416.2;437.5;688.4;1268.6;908.5;1589.2;706.2;1078.4;644.0;1088.0;745.7;487.4;1511.0;1809.0;514.2;2249.7;1887.4;1454.4;1659.5;634.7;1271.7;1757.5;1335.1;1433.7;481.7;3528.4;427.9;1972.2;450.4;379.2;1485.4;592.2;1454.0;1926.5;1407.7;1711.4;457.6;1472.7;1233.9;334.0;1194.0;486.2;208.4;489.1;359.7;593.1;1260.0;773.9;557.6;413.1;424.9;2327.5;412.2;2466.2;1436.0;747.1;1036.9;598.0;385.5;446.5;1128.5;437.0;521.2;1657.9;2494.4;2969.0;323.9;454.4;1210.6;558.1;431.6;400.5;478.4;533.2;448.1;305.6;344.0;485.0;1545.1;1802.5;346.9;2029.2;724.4;665.6;972.5;1052.2;1917.9;344.0;1549.4;2871.9;936.4;628.2;814.7;445.2;470.5;762.2;398.9;376.7;2524.6;826.1;352.1;433.0;1038.5;1699.2;430.1;1678.4;393.4;655.9;1387.1;1187.0;1946.2;1922.0;444.2;415.2;761.1;1542.0;1440.6;2092.0;788.0;504.4;468.9;928.6;987.4;568.6;727.6;520.7;860.7;428.2;494.4;786.6;435.9;2489.5;1295.0;680.4;828.2;1068.2;800.2;525.1;419.9;2697.2;691.4;771.1;515.0;1561.0;2562.5;2428.1;2726.0;554.0;3090.9;2571.1;530.9;500.4;640.1;762.5;1223.2;368.4;436.1;406.5;2014.5;1847.2;149.1;304.4;1016.5;1669.0;206.4;703.2;446.4;486.2;1179.1;1977.0;1871.6;928.4;559.4;1503.6;1034.7;440.5;481.0;432.0;446.0;314.0;

    stn;time;leadtime;T_2M;T_2M;T_2M;T_2M;T_2M;T_2M;T_2M;T_2M;T_2M;T_2M;T_2M;T_2M;T_2M;T_2M;T_2M;T_2M;T_2M;T_2M;T_2M;T_2M;T_2M;FF_10M;FF_10M;FF_10M;FF_10M;FF_10M;FF_10M;FF_10M;FF_10M;FF_10M;FF_10M;FF_10M;FF_10M;FF_10M;FF_10M;FF_10M;FF_10M;FF_10M;FF_10M;FF_10M;FF_10M;FF_10M;DD_10M;DD_10M;DD_10M;DD_10M;DD_10M;DD_10M;DD_10M;DD_10M;DD_10M;DD_10M;DD_10M;DD_10M;DD_10M;DD_10M;DD_10M;DD_10M;DD_10M;DD_10M;DD_10M;DD_10M;DD_10M;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;TOT_PREC;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;RELHUM_2M;DURSUN;DURSUN;DURSUN;DURSUN;DURSUN;DURSUN;DURSUN;DURSUN;DURSUN;DURSUN;DURSUN;DURSUN;DURSUN;DURSUN;DURSUN;DURSUN;DURSUN;DURSUN;DURSUN;DURSUN;DURSUN;
    ;unit;;[deg C];[deg C];[deg C];[deg C];[deg C];[deg C];[deg C];[deg C];[deg C];[deg C];[deg C];[deg C];[deg C];[deg C];[deg C];[deg C];[deg C];[deg C];[deg C];[deg C];[deg C];[m s-1];[m s-1];[m s-1];[m s-1];[m s-1];[m s-1];[m s-1];[m s-1];[m s-1];[m s-1];[m s-1];[m s-1];[m s-1];[m s-1];[m s-1];[m s-1];[m s-1];[m s-1];[m s-1];[m s-1];[m s-1];[degrees];[degrees];[degrees];[degrees];[degrees];[degrees];[degrees];[degrees];[degrees];[degrees];[degrees];[degrees];[degrees];[degrees];[degrees];[degrees];[degrees];[degrees];[degrees];[degrees];[degrees];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[kg m-2];[%];[%];[%];[%];[%];[%];[%];[%];[%];[%];[%];[%];[%];[%];[%];[%];[%];[%];[%];[%];[%];[s];[s];[s];[s];[s];[s];[s];[s];[s];[s];[s];[s];[s];[s];[s];[s];[s];[s];[s];[s];[s];
    ;member;;00;01;02;03;04;05;06;07;08;09;10;11;12;13;14;15;16;17;18;19;20;00;01;02;03;04;05;06;07;08;09;10;11;12;13;14;15;16;17;18;19;20;00;01;02;03;04;05;06;07;08;09;10;11;12;13;14;15;16;17;18;19;20;00;01;02;03;04;05;06;07;08;09;10;11;12;13;14;15;16;17;18;19;20;00;01;02;03;04;05;06;07;08;09;10;11;12;13;14;15;16;17;18;19;20;00;01;02;03;04;05;06;07;08;09;10;11;12;13;14;15;16;17;18;19;20;
    '''
        file.write(text_to_add)
        for abr in abr_list:
            for i in range(21):
                date = now_rounded + timedelta(hours=96-i*6) - timedelta(days=3)
                file.write(f'{abr};')
                file.write(f'{date.strftime("%Y%m%d %H:%M")};')

                leadtime_date = now_rounded + timedelta(hours=6*i)
                total_hours = 6 * i
                minutes = leadtime_date.strftime("%M")
                file.write(f'{total_hours:03d}:{minutes};')

                for j in range(126):
                    file.write(f'-;')
                file.write('\n')

def cosmo_parser(station_abr: str, wind_speed_coef: float, raw: bool):
    try:
        if raw == True:
            raw = True
        else:
            raw = False
    except:
        raw = False
    if wind_speed_coef == 1:
        unit = ' km/h'
    else:
        unit = ' noeuds'
    try:
        urllib.request.urlretrieve(URL_COSMO, 'COSMO-E-all-stations.csv')
    except urllib.error.URLError:
        create_cosmo_errored_file()

    header_to_remove = ['stn', 'time', 'leadtime', 'unit', 'member', '']
    content = open('COSMO-E-all-stations.csv', 'r').read()
    amout_of_line_to_skip = 23

    content = content.split('\n')[amout_of_line_to_skip:]

    first_row = content[0:3]
    first_row_ = ''

    for i in first_row:
        first_row_ = first_row_ + i
    first_row = first_row_
    first_row = first_row_.split(';')


    new_first_row = []
    for i in first_row:
        if i not in header_to_remove:
            new_first_row.append(i)


    fieldnames = ['stn', 'time', 'leadtime'] 
    for count, i in enumerate(new_first_row[:int(len(new_first_row)/3)]):
        name = i + '_' + new_first_row[int(count+2*len(new_first_row)/3)]
        fieldnames.append(name)
    fieldnames = ';'.join(fieldnames)

    del content[0:3]
    content.insert(0, fieldnames)
    content = '\n'.join(content)

    content = StringIO(content)
    csv_reader = csv.DictReader(content, delimiter=';')

    if not raw:
        data = [['Date', 'Moyenne', 'Médiane', 'Minimum', 'Maximum']]
    else:
        data = []
    for row in csv_reader:
        if row['stn'].upper() == station_abr.upper():
            values = []
            for i in range(20):
                i = str(i).zfill(2)
                values.append(float(row[f'FF_10M_{i}'])*3.6)
            time = datetime.strptime(row['time'], '%Y%m%d %H:%M')
            values.sort()
            mean = numpy.mean(values)
            median = numpy.median(values)
            # print(f'{time}    median: {round(median*wind_speed_coef)}  min: {round(min(values)*wind_speed_coef, 1)}  max: {round(max(values)*wind_speed_coef, 1)}')
            if not raw:
                time = time.strftime('%d/%m/%Y %Hh')
                data.append([time, round(mean*wind_speed_coef, 1), round(median*wind_speed_coef, 1), round(min(values)*wind_speed_coef, 1), str(round(max(values)*wind_speed_coef, 1)) + unit])
            else:
                values = values[2:-2]
                time = time.strftime('%d/%m %Hh')
                data.append([time, round(median*wind_speed_coef, 1), round(min(values)*wind_speed_coef, 1), round(max(values)*wind_speed_coef, 1)])
            print(f'{time}    moy: {round(mean*wind_speed_coef, 1)}  median: {round(median*wind_speed_coef, 1)}  min: {round(min(values)*wind_speed_coef, 1)}  max: {round(max(values)*wind_speed_coef, 1)}')
    return data

if __name__ == '__main__':
    abr = input('abréviation ? : ')
    cosmo_parser(abr, wind_speed_coef=1, raw=False)
