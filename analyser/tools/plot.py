import asyncio
import argparse
from datetime import datetime, timedelta
from matplotlib import cm, ticker
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from settings import DB, LOGGER, MONGO_COLLECTION_INTEREST, MONGO_COLLECTION_DATA, \
    MONGO_COLLECTION_LP_PACKET_INTEREST, MONGO_COLLECTION_LP_PACKET_DATA


class Plot:
    SCATTER = 'scatter'
    BAR = 'bar'
    CDF = 'cdf'

    def __init__(self, db, collections):
        self.db = db
        self.collections = collections

    async def components_cdf(self):
        interests = self.db[self.collections['INTEREST']]
        data = self.db[self.collections['DATA']]
        lp_interest = self.db[self.collections['LP_PACKET_INTEREST']]
        lp_data = self.db[self.collections['LP_PACKET_DATA']]
        i_num_components = []
        d_num_components = []
        lp_interest_num_components = []
        lp_data_num_components = []

        async for interest in interests.find():
            i_num_components.append(len(
                interest['_source']['layers']['ndn']['ndn_name_tree']['ndn_genericnamecomponent']))
        async for d in data.find():
            d_num_components.append(len(
                d['_source']['layers']['ndn']['ndn_name_tree']['ndn_genericnamecomponent']))
        async for lp_interest in lp_interest.find():
            lp_interest_num_components.append(len(
                lp_interest['_source']['layers']['ndn'][1]['ndn_name_tree']['ndn_genericnamecomponent']))
        async for lp_data in lp_data.find():
            lp_data_num_components.append(len(
                lp_data['_source']['layers']['ndn'][1]['ndn_name_tree']['ndn_genericnamecomponent']))

        i_num_components += lp_interest_num_components
        d_num_components += lp_data_num_components

        i_counts, i_bin_edges = np.histogram(
            i_num_components, bins=np.arange(1, max(i_num_components)+1))
        i_cdf = np.cumsum(i_counts)
        i_cdf = i_cdf / i_cdf[-1]

        d_counts, d_bin_edges = np.histogram(
            d_num_components, bins=np.arange(1, max(d_num_components)+1))
        d_cdf = np.cumsum(d_counts)
        d_cdf = d_cdf / d_cdf[-1]

        _, ax = plt.subplots(figsize=(10, 7))
        ax.plot(i_bin_edges[:-1], i_cdf, label='Interest')
        ax.plot(d_bin_edges[:-1], d_cdf, label='Data')

        ax.set_title('Name Components CDF', fontsize=20)
        ax.set_xlabel('Number of Components', fontsize=16)
        ax.set_ylabel('Percentile', fontsize=16)
        ax.tick_params(labelsize=14)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_linewidth(0.5)
        ax.spines['left'].set_linewidth(0.5)
        ax.legend()
        plt.show()

    async def packets_per_duration(self, plot_type, duration):
        i_ts = []
        d_ts = []
        for collection in self.collections.values():
            pipeline = [
                {'$project': {
                    '_id': 0, 'frame_time_epoch': '$_source.layers.frame.frame_time_epoch'}},
                {'$sort': {'frame_time_epoch': 1}}
            ]
            r = self.db[collection].aggregate(pipeline)
            timestamps = []
            async for doc in r:
                timestamps.append(int(float(doc['frame_time_epoch']) * 1e9))

            if collection == self.collections['INTEREST']:
                i_ts = i_ts + timestamps if i_ts else timestamps
            elif collection == self.collections['DATA']:
                d_ts = d_ts + timestamps if d_ts else timestamps
            elif collection == self.collections['LP_PACKET_INTEREST']:
                i_ts = i_ts + timestamps if i_ts else timestamps
            elif collection == self.collections['LP_PACKET_DATA']:
                d_ts = d_ts + timestamps if d_ts else timestamps

        # count number of packets in each duration
        start_time = datetime.fromtimestamp(min(i_ts[0], d_ts[0]) / 1e9)
        end_time = datetime.fromtimestamp(max(i_ts[-1], d_ts[-1]) / 1e9)
        d = int((end_time - start_time).total_seconds())
        num_durations = d // (duration * 60) + 1

        interest_num_packets = [0] * num_durations
        interest_ts = [0] * num_durations
        data_num_packets = [0] * num_durations
        data_ts = [0] * num_durations

        for packet_t in i_ts:
            packet_duration = int((datetime.fromtimestamp(
                packet_t / 1e9) - start_time).total_seconds() // (duration * 60))
            interest_num_packets[packet_duration] += 1
            interest_ts[packet_duration] = datetime.fromtimestamp(
                packet_t / 1e9)
        for packet_t in d_ts:
            packet_duration = int((datetime.fromtimestamp(
                packet_t / 1e9) - start_time).total_seconds() // (duration * 60))
            data_num_packets[packet_duration] += 1
            data_ts[packet_duration] = datetime.fromtimestamp(
                packet_t / 1e9)

        # plot
        _, ax = plt.subplots(figsize=(10, 7))
        if plot_type == Plot.BAR:
            rshift = 1
            ax.bar(np.arange(num_durations) + rshift / 2, interest_num_packets,
                   color=cm.Paired(0), label='Interest packets')
            ax.bar(np.arange(num_durations) + rshift / 2,
                   data_num_packets, color=cm.Paired(1), label='Data packets')
            duration_labels = [(start_time + timedelta(minutes=i * duration)).strftime('%-I %p')
                               for i in range(num_durations + rshift)]
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(
                lambda x, pos: duration_labels[int(x)] if x < len(duration_labels) else ''))

        elif plot_type == Plot.SCATTER:
            ax.scatter(interest_ts, interest_num_packets,
                       label='Interest packets')
            ax.scatter(data_ts, data_num_packets, label='Data packets')
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%-I %p'))

        ax.set_title(f'Packets received per {duration} minutes')
        ax.set_xlabel('Timestamp')
        ax.set_ylabel(f'Packets per {duration} minutes')
        ax.legend()
        plt.show()

    async def plot(self, plot_type, duration):
        if plot_type in [self.BAR, self.SCATTER]:
            await self.packets_per_duration(plot_type, duration)
        elif plot_type == self.CDF:
            await self.components_cdf()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Plot NDN packet statistics.', prog='python -m tools.plot')
    parser.add_argument('--plot_type', default=Plot.SCATTER, choices=[Plot.SCATTER, Plot.BAR, Plot.CDF],
                        help=f'Type of plot to generate (available: {", ".join([Plot.SCATTER, Plot.BAR, Plot.CDF])}))')
    parser.add_argument('--duration', default=60, type=int,
                        help='Duration in minutes to group packets (default: 60) (applicable only for "scatter" and "bar" plots)')
    args = parser.parse_args()

    if args.plot_type in [Plot.SCATTER, Plot.BAR] and args.duration <= 0:
        LOGGER.error(
            f'Error: Invalid duration provided for {args.plot_type} plot')
        exit(1)

    plot = Plot(DB, {'INTEREST': MONGO_COLLECTION_INTEREST, 'DATA': MONGO_COLLECTION_DATA,
                     'LP_PACKET_INTEREST': MONGO_COLLECTION_LP_PACKET_INTEREST, 'LP_PACKET_DATA': MONGO_COLLECTION_LP_PACKET_DATA})

    asyncio.run(plot.plot(args.plot_type, args.duration))