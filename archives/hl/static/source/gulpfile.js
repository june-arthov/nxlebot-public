var gulp = require('gulp'),
    postcss = require('gulp-postcss'),
    sass = require('gulp-sass'),
    rename = require('gulp-rename'),
    sourcemaps = require('gulp-sourcemaps'),
    concat = require('gulp-concat'),
    autoprefixer = require('autoprefixer'),
    cssnano = require('gulp-cssnano');

gulp.task('css', function() {
    return gulp.src('scss/hl.scss')
        //.pipe(sourcemaps.init())
        .pipe(sass({ precision: 10 }))
        .pipe(postcss([ autoprefixer({ browsers: [
            "Android 2.3",
            "Android >= 4",
            "Chrome >= 20",
            "Firefox >= 24",
            "Explorer >= 8",
            "iOS >= 6",
            "Opera >= 12",
            "Safari >= 6"
        ] }) ]))
        //.pipe(sourcemaps.write('.'))
        .pipe(gulp.dest('../css/'))
        .pipe(cssnano())
        .pipe(rename({ extname: '.min.css' }))
        .pipe(gulp.dest('../css/'));
});


gulp.task('watch', function() {
    var watcher = gulp.watch('scss/*', ['css']);

    watcher.on('change', function (event) {
        console.log('File ' + event.path + ' was ' + event.type + '. Now running css task...');
    });
});
