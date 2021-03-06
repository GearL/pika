from datetime import datetime

from cms.models import db, ModelMixin


class Category(ModelMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    urlstr = db.Column(db.String(16))
    articles = db.relationship('Article', backref='category')

    def __str__(self):
        return "%s" % self.name

    def __repr__(self):
        return "<Category %s>" % self.name

    def delete(self, commit=True):
        for article in self.articles:
            article.delete(False)
        db.session.add(self)
        if commit:
            db.session.commit()


class Article(ModelMixin, db.Model):

    __tablename__ = 'article'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    description = db.Column(db.Text)
    create_date = db.Column(db.DateTime, default=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    deleted = db.Column(db.BOOLEAN, default=False)

    def delete(self, commit=True):
        self.deleted = True
        db.session.add(self)
        if commit:
            db.session.commit()

    def __str__(self):
        return ("%s" % self.name)

    def __repr__(self):
        return "<Article %s>" % self.name
