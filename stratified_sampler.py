#!/usr/bin/env python3
import sys
import pandas as pd
import yaml
from datetime import datetime

class ArticleRandomizer:
    def __init__(self):
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        self.article_file= config['initial_settings']['input_file']
        self.random_seed = config['initial_settings']['random_seed']
        self.output_file = config['initial_settings']['output_file']
        self.target_n = config['initial_settings']['target_sample_size']
        self.periods = config['time_periods']['periods']
        self.categories = config['category_groups']['categories']
        self.combinations = len(self.periods) * len(self.categories) #using len() for count in each instance attribute
        self.target_per_category = self.target_n // self.combinations


        # Presidential admin periods
        self.admin_periods = {}
        for name, period in config['time_periods']['periods'].items():
            self.admin_periods[name] = {
                'start': datetime.strptime(period['start'], '%Y-%m-%d'),
                'end': datetime.strptime(period['end'], '%Y-%m-%d')
            }

    def classify_source_bias(self, publication): #change to classify category
        if not isinstance(publication, str) or not publication.strip():
            return 'Unknown'
        pub_lower = publication.lower()

        for bias, sources in self.categories.items():
            for source in sources:
                if source.lower() in pub_lower or pub_lower in source.lower():
                    return bias
        return 'Unknown'

    def assign_admin(self, article_date):   #change to assign time period?
        if getattr(article_date, 'tzinfo', None) is not None:
            article_date = article_date.replace(tzinfo=None)
        for admin, period in self.admin_periods.items():
            if period['start'] <= article_date <= period['end']:
                return admin
        return 'Excluded'

    def load_and_prepare_data(self):
        df = pd.read_excel(self.article_file)
        df['Date'] = pd.to_datetime(df['Date'])
        df['Political_Bias'] = df['Source'].apply(self.classify_source_bias)
        df['Administration'] = df['Date'].apply(self.assign_admin)

        before_exclusion = len(df)
        df = df[df['Administration'] != 'Excluded'] #outside years
        excluded_count = before_exclusion - len(df)
        if excluded_count > 0:
            print(f"Excluded {excluded_count} articles outside administration periods")
        df = df[df['Political_Bias'] != 'Unknown'] #sources not in list
        print(f"Data loaded: {len(df)} articles after removing unknown bias sources")
        print(f"Bias distribution in articles:")
        print(df['Political_Bias'].value_counts())
        print(f"Administration distribution in articles:")
        print(df['Administration'].value_counts())
        return df

    def randomized_sample_by_admin_bias(self, df):
        selected_articles = []
        target_per_bias = self.target_per_category
        print(f"\n{'=' * 60}")
        print("RANDOMIZED SAMPLING BY ADMINISTRATION AND BIAS")
        print(f"{'=' * 60}")

        for admin in self.admin_periods:
            admin_data = df[df['Administration'] == admin]
            if len(admin_data) == 0:
                print(f"\nWARNING: No articles found for {admin}")
                continue

            print(f"\n{admin.upper()} ADMINISTRATION:")
            print(f"Total articles available: {len(admin_data)}")

            admin_sample = []

            for bias in self.categories:
                bias_data = admin_data[admin_data['Political_Bias'] == bias]
                if len(bias_data) == 0:
                    print(f"  {bias}: No articles available")

                    continue

                # Random sample from this bias category
                if len(bias_data) >= target_per_bias:
                    sampled = bias_data.sample(n=target_per_bias, random_state=self.random_seed)
                    selected_count = target_per_bias
                else:
                    sampled = bias_data
                    selected_count = len(bias_data)
                    print(f"  WARNING: {bias} stratum under target — only {len(bias_data)} available")
                admin_sample.append(sampled)
                print(f"  {bias}: Selected {selected_count} from {len(bias_data)} available")

            if admin_sample:
                admin_combined = pd.concat(admin_sample)
                selected_articles.append(admin_combined)
                print(f"  TOTAL for {admin}: {len(admin_combined)} articles")

        # Combine articles
        if selected_articles:
            final_sample = pd.concat(selected_articles)
        else:
            final_sample = pd.DataFrame()
        print(f"\n{'=' * 60}")
        print(f"FINAL SAMPLE SIZE: {len(final_sample)} articles")
        print(f"TARGET SIZE: {self.target_n} articles")

        #Randomize
        if len(final_sample) > self.target_n:
            print(f"Randomly reducing sample to target size...")
            final_sample = final_sample.sample(n=self.target_n, random_state=self.random_seed)

        #if not enough articles, identify & re-randomize remaining
        elif len(final_sample) < self.target_n:
            shortage = self.target_n - len(final_sample)
            print(f"Short by {shortage} articles - adding from remaining articles...")
            remaining = df[~df.index.isin(final_sample.index)]
            if len(remaining) >= shortage:
                additional = remaining.sample(n=shortage, random_state=self.random_seed)
                final_sample = pd.concat([final_sample, additional])
        return final_sample.reset_index(drop=True)


    def run_sampling(self):
        try:
            # Load
            df = self.load_and_prepare_data()
            sample_df = self.randomized_sample_by_admin_bias(df)
            if len(sample_df) == 0:
                print("ERROR: No articles selected. Check data and bias classifications.")
                return None
            # Save to excel
            sample_df.to_excel(self.output_file, index=False)
            print(f"\nSample saved to:")
            print(f"  {self.output_file}")
            print(f"\nSampling complete! Final sample: {len(sample_df)} articles")
            return sample_df
        except Exception as e:
            print(f"ERROR during sampling: {e}")
            return None


if __name__ == "__main__":
    print("Stratified Sampling Tool")
    print ("Version 1.0")
    print("=" * 60)
    try:
        sampler = ArticleRandomizer()
        sample_df = sampler.run_sampling ()#run
       
        if sample_df is not None:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except FileNotFoundError:
        print(f"ERROR: Required file not found.")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")

