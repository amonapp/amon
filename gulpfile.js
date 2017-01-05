var gulp = require('gulp');
var sass = require('gulp-sass');
var uglify = require('gulp-uglify');
var concat = require('gulp-concat');
var ngAnnotate = require('gulp-ng-annotate')
 
gulp.task('sass', function () {
  gulp.src('amon/static/sass/**/*.scss')
	.pipe(sass().on('error', sass.logError))
	.pipe(sass({outputStyle: 'compressed'}))
	.pipe(gulp.dest('amon/static/css'));
});
 
gulp.task('sass:watch', function () {
  gulp.watch('amon/static/sass/**/*.scss', ['sass']);
});


gulp.task('js', function () {
  gulp.src(['amon/static/js/apps/*.js'])
    .pipe(concat('app.min.js'))
    .pipe(ngAnnotate())
    .pipe(uglify())
    .pipe(gulp.dest('amon/static/js/'))
})