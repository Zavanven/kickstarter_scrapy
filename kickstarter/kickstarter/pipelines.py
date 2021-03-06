# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3


class KickstarterPipeline:
    def open_spider(self, spider):
        self.connection = sqlite3.connect('kickstarter.db')
        self.cursor = self.connection.cursor()
        try:
            self.cursor.execute('''
                CREATE TABLE projects(
                    project_name TEXT,
                    project_state TEXT,
                    backers_count INTEGER,
                    project_pledged REAL,
                    percent_raised REAL,
                    project_url TEXT,
                    description TEXT,
                    profile_name TEXT,
                    profile_url TEXT,
                    category TEXT,
                    country TEXT,
                    unique (project_name)
                )
            ''')
            self.connection.commit()
        except sqlite3.OperationalError:
            pass

    def process_item(self, item, spider):
        self.cursor.execute(
            '''
            INSERT OR REPLACE INTO projects (
                project_name,
                project_state,
                backers_count,
                project_pledged,
                percent_raised,
                project_url,
                description,
                profile_name,
                profile_url,
                category,
                country
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
            '''
        , (
            item.get('project_name'),
            item.get('project_state'),
            int(item.get('backers_count')),
            round(float(item.get('project_pledged')), 2),
            round(float(item.get('percent_raised')), 2),
            item.get('project_url'),
            item.get('description'),
            item.get('profile_name'),
            item.get('profile_url'),
            item.get('category'),
            item.get('country'),
        ))
        self.connection.commit()
        return item

    def close_spider(self, spider):
        self.connection.close()