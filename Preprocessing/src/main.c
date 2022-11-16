#include<string.h>
#include<stdlib.h>

#include <stdio.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/types.h>

#include <unistd.h>
#include <pthread.h>
#include <time.h>
#include <stdbool.h>

#include <ta-lib/ta_libc.h>

#define MAX_LINE_LENGTH 80
#define CSV_LENGTH 525601

struct indicators {
    
};

struct candle {
    long time;
    double open;
    double close;
    double high;
    double low;
    double volume;

    double adosc;
    double atr;

    double bb_upper;
    double bb_middle;
    double bb_lower;

    double macd;
    double macd_signal;
    double macd_hist;

    double mfi;
    double rsi;
    double sar;
    double tema;
};

struct indicator_selection {
    // adsoc, atr, bb_upper, bb_middel, bb_lower, macd, mfi, rsi, sar, tema
    bool adosc;
    bool atr;
    bool bb;
    bool macd;
    bool mfi;
    bool rsi;
    bool sar;
    bool tema;
};

struct indicator_thread {
    char *input_file;
    char *output_file;
};

double normalize(double a1, double a2) {
    return a1 == 0 ? a1 : (a2 - a1) / a1;
};

void calculate_indicators(struct indicator_selection *selection, struct candle *candles, char * output_file[]) {
    // adsoc, atr, bb_upper, bb_middel, bb_lower, macd, mfi, rsi, sar, tema
    
    double *temp_open = malloc(sizeof(double) * CSV_LENGTH);
    double *temp_high = malloc(sizeof(double) * CSV_LENGTH);
    double *temp_low = malloc(sizeof(double) * CSV_LENGTH);
    double *temp_close = malloc(sizeof(double) * CSV_LENGTH);
    double *temp_volume = malloc(sizeof(double) * CSV_LENGTH);

    for (int i = 0; i < CSV_LENGTH - 1 ; i++)
    {
        struct candle *candle = &candles[i];

        temp_open[i] = candle->open;
        temp_high[i] = candle->high;
        temp_low[i] = candle->low;
        temp_close[i] = candle->close;
        temp_volume[i] = candle->volume;
    }

    // free(candles);

    double *tmp_adosc = malloc(sizeof(double) * CSV_LENGTH);
    double *tmp_atr = malloc(sizeof(double) * CSV_LENGTH);

    double *tmp_bb_upper = malloc(sizeof(double) * CSV_LENGTH);
    double *tmp_bb_middle = malloc(sizeof(double) * CSV_LENGTH);
    double *tmp_bb_lower = malloc(sizeof(double) * CSV_LENGTH);

    double *tmp_macd = malloc(sizeof(double) * CSV_LENGTH);
    double *tmp_macd_signal = malloc(sizeof(double) * CSV_LENGTH);
    double *tmp_macd_hist = malloc(sizeof(double) * CSV_LENGTH);

    double *tmp_mfi = malloc(sizeof(double) * CSV_LENGTH);
    double *tmp_rsi = malloc(sizeof(double) * CSV_LENGTH);
    double *tmp_sar = malloc(sizeof(double) * CSV_LENGTH);
    double *tmp_tema = malloc(sizeof(double) * CSV_LENGTH);


    int beginIdx, endIdx;

    if (selection->adosc)
        TA_ADOSC(0, CSV_LENGTH - 1, temp_high, temp_low, temp_close, temp_volume, 3, 10, &beginIdx, &endIdx, tmp_adosc);

    if (selection->atr)
        TA_ATR(0, CSV_LENGTH - 1, temp_high, temp_low, temp_close, 14, &beginIdx, &endIdx, tmp_atr);

    if (selection->bb)
        TA_BBANDS(0, CSV_LENGTH - 1, temp_close, 20, 2, 2, TA_MAType_SMA, &beginIdx, &endIdx, tmp_bb_upper, tmp_bb_middle, tmp_bb_lower);

    if (selection->macd)
        TA_MACD(0, CSV_LENGTH - 1, temp_close, 12, 26, 9, &beginIdx, &endIdx, tmp_macd, tmp_macd_signal, tmp_macd_hist);

    if (selection->mfi)
        TA_MFI(0, CSV_LENGTH - 1, temp_high, temp_low, temp_close, temp_volume, 14, &beginIdx, &endIdx, tmp_mfi);
    
    if (selection->rsi)
        TA_RSI(0, CSV_LENGTH - 1, temp_close, 14, &beginIdx, &endIdx, tmp_rsi);

    if (selection->sar)
        TA_SAR(0, CSV_LENGTH - 1, temp_high, temp_low, 0.02, 0.2, &beginIdx, &endIdx, tmp_sar);

    if (selection->tema)
        TA_TEMA(0, CSV_LENGTH - 1, temp_close, 30, &beginIdx, &endIdx, tmp_tema);



    // Assign the calculated values to the candles
    for (int i = 0; i < CSV_LENGTH; i++)
    {
        struct candle *candle = &candles[i];

        if (selection->adosc)
            candle->adosc = tmp_adosc[i];

        if (selection->atr)
            candle->atr = tmp_atr[i];

        if (selection->bb)
        {
            candle->bb_upper = tmp_bb_upper[i];
            candle->bb_middle = tmp_bb_middle[i];
            candle->bb_lower = tmp_bb_lower[i];
        }

        if (selection->macd)
        {
            candle->macd = tmp_macd[i];
            candle->macd_signal = tmp_macd_signal[i];
            candle->macd_hist = tmp_macd_hist[i];
        }

        if (selection->mfi)
            candle->mfi = tmp_mfi[i];
        
        if (selection->rsi)
            candle->rsi = tmp_rsi[i];

        if (selection->sar)
            candle->sar = tmp_sar[i];

        if (selection->tema)
            candle->tema = tmp_tema[i];
    }

    free(temp_open);
    free(temp_high);
    free(temp_low);
    free(temp_close);
    free(temp_volume);



    struct candle *new_candles;


    // length of allocation is one year in minutes (minute candles)
    new_candles = calloc(CSV_LENGTH, sizeof(struct candle));

    FILE *wfp = fopen(output_file, "a");
    for (size_t i = 0; i < CSV_LENGTH - 1 ; i++) {
        if (i == 0)
            fprintf(wfp, "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n", "event_time","open","close","high","low","volume","adosc", "atr", "bb_upper", "bb_middle", "bb_lower", "macd", "macd_signal", "macd_hist", "mfi", "rsi", "sar", "tema");
        else {
            struct candle *candle = &candles[i];
            struct candle *new_candle = &new_candles[i];

            new_candle->time = candle->time;

            if (i > 0) {
                // Normalize candle
                new_candle->open = normalize(candle->open, candles[i - 1].close);
                new_candle->close = normalize(candle->close, candles[i - 1].close);
                new_candle->high = normalize(candle->high, candles[i - 1].close);
                new_candle->low = normalize(candle->low, candles[i - 1].close);
                new_candle->volume = normalize(candle->volume, candles[i - 1].volume);

                new_candle->adosc = normalize(candle->adosc, candles[i - 1].adosc);
                new_candle->atr = normalize(candle->atr, candles[i - 1].atr);

                new_candle->bb_upper = normalize(candle->bb_upper, candles[i - 1].bb_upper);
                new_candle->bb_middle = normalize(candle->bb_middle, candles[i - 1].bb_middle);
                new_candle->bb_lower = normalize(candle->bb_lower, candles[i - 1].bb_lower);

                new_candle->macd = normalize(candle->macd, candles[i - 1].macd);
                new_candle->macd_signal = normalize(candle->macd_signal, candles[i - 1].macd_signal);
                new_candle->macd_hist = normalize(candle->macd_hist, candles[i - 1].macd_hist);

                new_candle->mfi /= 100;
                new_candle->rsi /= 100;
                new_candle->sar = normalize(candle->sar, candles[i - 1].sar);
                new_candle->tema = normalize(candle->tema, candles[i - 1].tema);

            }

            fprintf(wfp, "%ld,%.8lf,%.8lf,%.8lf,%.8lf,%.8lf,%.8lf,%.8lf,%.8lf,%.8lf,%.8lf,%.8lf,%.8lf,%.8lf,%.8lf,%.8lf,%.8lf,%.8lf\n", 
                new_candle->time, 
                new_candle->open, 
                new_candle->close, 
                new_candle->high, 
                new_candle->low, 
                new_candle->volume, 
                new_candle->adosc,
                new_candle->atr,
                new_candle->bb_upper,
                new_candle->bb_middle,
                new_candle->bb_lower,
                new_candle->macd,
                new_candle->macd_signal,
                new_candle->macd_hist,
                new_candle->mfi,
                new_candle->rsi,
                new_candle->sar,
                new_candle->tema
            );


        }
    }

    fclose(wfp);

    free(tmp_adosc);
    free(tmp_atr);
    free(tmp_bb_upper);
    free(tmp_bb_middle);
    free(tmp_bb_lower);
    free(tmp_macd);
    free(tmp_macd_signal);
    free(tmp_macd_hist);
    free(tmp_mfi);
    free(tmp_rsi);
    free(tmp_sar);
    free(tmp_tema);

};

void *prepocess(void* args) {
    struct indicator_thread *thread_args = args;

    char *filename_qfd = thread_args->input_file;

    char *output_file = thread_args->output_file;

    char str[MAX_LINE_LENGTH];
    int result;
    FILE *fp = fopen(filename_qfd, "r");

    struct candle *candles;


    // length of allocation is one year in minutes (minute candles)
    candles = calloc(CSV_LENGTH, sizeof(struct candle));
    // print size of struct candle
    if (candles == NULL) 
    {
        printf("Error allocating memory for candles\n");
        exit(1);
    }

    int count = 0;
    while (fgets(str, MAX_LINE_LENGTH, fp)) 
    {
        struct candle *c = (struct candle *)&candles[count - 1];
        sscanf(str, "%ld,%lf,%lf,%lf,%lf,%lf", &c->time, &c->open, &c->close, &c->high, &c->low, &c->volume);
        count++;
    }

    struct indicator_selection selection;

    // Chaikin Oscillator - Momentum indicator
    selection.adosc = true; // Above 0 net buying pressure, below 0 net selling pressure


    // High volatility are considered as high risk,yet we love volatility, it can create fear, and puts great assets on sale
    // Averate True Range - Volatility (strength of price action) indicator
    selection.atr = true;

    // Bollinger Bands - Volatility indicator
    selection.bb = true; // How close the upper and lower band are at any given time illustrates the degree of volatility the price is experiencing.
    
    // Moving Average Convergence Divergence - Momentum indicator
    selection.macd = true;

    // Money Flow Index - Volume indicator
    selection.mfi = true;
    selection.rsi = true;
    selection.sar = true;
    selection.tema = true;

    calculate_indicators(&selection, candles, output_file);

    fclose(fp);
    free(candles);
    printf("Finished file: %s\n", output_file);
}

int countfiles(char *path) {
    DIR *dir_ptr = NULL;
    struct dirent *direntp;
    char *npath;
    if (!path) return 0;
    if( (dir_ptr = opendir(path)) == NULL ) return 0;

    int count=0;
    while( (direntp = readdir(dir_ptr)))
    {
        if (strcmp(direntp->d_name,".")==0 ||
            strcmp(direntp->d_name,"..")==0) continue;
        switch (direntp->d_type) {
            case DT_REG:
                ++count;
                break;
            case DT_DIR:            
                npath=malloc(strlen(path)+strlen(direntp->d_name)+2);
                sprintf(npath,"%s/%s",path, direntp->d_name);
                count += countfiles(npath);
                free(npath);
                break;
        }
    }
    closedir(dir_ptr);
    return count;
}

int main(int argc, char** argv)   // define the main function  
{  
    char *input_folder = argv[1];
    char *output_folder = argv[2];
    struct dirent *dp;
    DIR *dfd;

    if ((dfd = opendir(input_folder)) == NULL)
    {
        fprintf(stderr, "Can't open %s\n", input_folder);
        return 0;
    }


    int num_files = countfiles(input_folder);
    char filename_qfd[300] ;
    char new_name_qfd[300] ;

    pthread_t threads[num_files];

    int i = 0;
    while ((dp = readdir(dfd)) != NULL) {

        struct stat stbuf ;
        sprintf( filename_qfd , "%s%s",input_folder,dp->d_name) ;
        if( stat(filename_qfd,&stbuf ) == -1 )
        {
            printf("Unable to stat file: %s\n", filename_qfd) ;
            continue ;
        }
        if ( ( stbuf.st_mode & S_IFMT ) != S_IFDIR )
        {
            char *s = calloc(strlen(filename_qfd) + 1, sizeof(char));
            strcpy(s, filename_qfd);

            char *st = calloc(strlen(s) + 1, sizeof(char));
            strcpy(st, s);
            // printf("File: %s\n", s);

            char *filename_qfd = calloc(300, sizeof(char));
            char *new_name_qfd = calloc(300, sizeof(char));

            free(filename_qfd);
            free(new_name_qfd);

            char *token = strtok(s, "/");
            char file_name[10];

            while (token != NULL) {
                strcpy(file_name, token);
                token = strtok(NULL, "/");
            }

            char *output_file = calloc(300, sizeof(char));
            strcat(output_file, output_folder);
            strcat(output_file, file_name);

            struct indicator_thread *thread = malloc(sizeof(struct indicator_thread));
            thread->input_file = st;
            thread->output_file = output_file;

            free(s);
            pthread_create(&threads[i], NULL, prepocess, (void *)thread);
            i++;
        }
    }

    

    for (int j = 0; j < num_files; j++) {
        pthread_join(threads[j], NULL);
    }

    closedir(dfd);

    return 0;

}  